import asyncio
import json
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from googletrans import Translator
from django.conf import settings


BOT_TOKEN = "8348560606:AAEx2E_cAnUW6HD_b41YpoagJgpIVYcp2_k"          # <-- TOKEN qo‘ying
WEBAPP_URL = "https://freetranslatorbot-production.up.railway.app/"     # <-- Django WebApp URL

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

translator = Translator()
user_lang = {}   # {user_id: {"src": "uz", "dest": "en"}}


# ------------------------------------
#  TIL TANLASH MENYUSI
# ------------------------------------
def lang_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton("🇺🇿 Uzbek → 🇬🇧 English"),
                KeyboardButton("🇬🇧 English → 🇺🇿 Uzbek"),
            ],
            [
                KeyboardButton("🇺🇿 Uzbek → 🇷🇺 Russian"),
                KeyboardButton("🇷🇺 Russian → 🇺🇿 Uzbek"),
            ]
        ],
        resize_keyboard=True
    )


# ------------------------------------
#  INPUT YONIGA CHIQADIGAN WEBAPP TUGMA
# ------------------------------------
def webapp_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🌐 WebApp Translator",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ],
        resize_keyboard=True
    )


# ------------------------------------
#  START COMMAND
# ------------------------------------
@dp.message(Command("start"))
async def start(message: Message):

    await message.answer(
        "Assalomu alaykum! 👋\n"
        "WebApp orqali ham, bot orqali ham tarjima qilishingiz mumkin.\n\n"
        "👇 WebApp tugmasi input yonida chiqadi:",
        reply_markup=webapp_keyboard()
    )

    await message.answer(
        "👇 Endi til yo‘nalishini tanlang:",
        reply_markup=lang_menu()
    )


# ------------------------------------
#  HAR QANDAY XABARLAR UCHUN HANDLER
# ------------------------------------
@dp.message()
async def all_messages(message: Message):

    user_id = message.from_user.id

    # ------------------------------------
    #  WEBAPP'DAN KELGAN DATA
    # ------------------------------------
    if message.web_app_data:
        try:
            data = json.loads(message.web_app_data.data)

            # WebApp Translation
            if data.get("type") == "webapp_translation":
                text = data.get("text", "")
                src = data.get("src", "")
                dest = data.get("dest", "")

                await message.answer(
                    f"🌐 WebApp tarjimasi:\n\n"
                    f"📤 From: {src}\n"
                    f"📥 To: {dest}\n"
                    f"📝 Matn: {text}"
                )
                return

        except Exception:
            await message.answer(f"WebApp'dan ma'lumot keldi:\n{message.web_app_data.data}")
            return

    # ------------------------------------
    #  TIL YO‘NALISHINI TANLASH
    # ------------------------------------
    if "→" in message.text:
        langs = {
            "🇺🇿 Uzbek → 🇬🇧 English": ("uz", "en"),
            "🇬🇧 English → 🇺🇿 Uzbek": ("en", "uz"),
            "🇺🇿 Uzbek → 🇷🇺 Russian": ("uz", "ru"),
            "🇷🇺 Russian → 🇺🇿 Uzbek": ("ru", "uz"),
        }

        src, dest = langs[message.text]
        user_lang[user_id] = {"src": src, "dest": dest}

        await message.answer(
            f"✅ Tanlandi: {message.text}\n"
            f"Endi tarjima qilish uchun matn yuboring."
        )
        return

    # ------------------------------------
    #  AGAR YO‘NALISH TANLANMAGAN BO‘LSA
    # ------------------------------------
    if user_id not in user_lang:
        await message.answer("⛔ Avval til yo‘nalishini tanlang!", reply_markup=lang_menu())
        return

    # ------------------------------------
    #  BOT ICHIDA TARJIMA QILISH
    # ------------------------------------
    src = user_lang[user_id]["src"]
    dest = user_lang[user_id]["dest"]

    try:
        translated = translator.translate(message.text, src=src, dest=dest)
        await message.answer(f"🔄 Tarjima:\n\n{translated.text}")

    except Exception as e:
        await message.answer(f"Xato: {e}")
async def on_startup():
    webhook_url = settings.WEBHOOK_URL
    await bot.set_webhook(webhook_url)

# Django view dan chaqiriladigan update processor
async def process_update(request_body):
    update = Update(**request_body)
    await dp.feed_update(bot, update)