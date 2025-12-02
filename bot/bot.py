import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from googletrans import Translator

BOT_TOKEN = "8348560606:AAEx2E_cAnUW6HD_b41YpoagJgpIVYcp2_k"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

translator = Translator()

# Foydalanuvchi til yo‘nalishi {user_id: {src: 'uz', dest: 'en'}}
user_lang = {}


# Til tanlash menyusi
def lang_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇺🇿 Uzbek → 🇷🇺 Russian"),
                KeyboardButton(text="🇷🇺 Russian → 🇺🇿 Uzbek"),
            ],
            [
                KeyboardButton(text="🇺🇿 Uzbek → 🇬🇧 English"),
                KeyboardButton(text="🇬🇧 English → 🇺🇿 Uzbek"),
            ],
            [
                KeyboardButton(text="WebApp Tarjimonni ochish")
            ]
        ],
        resize_keyboard=True
    )
    return kb


@dp.message(Command("start"))
async def start_cmd(message: Message):

    # INPUT yoniga chiqadigan WebApp tugma
    input_webapp = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🌐 WebApp Translator",
                    web_app=WebAppInfo(url="https://YOUR-DOMAIN.COM")
                )
            ]
        ],
        resize_keyboard=True
    )

    # Til tanlash menyusi
    langs = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇺🇿 Uzbek → 🇷🇺 Russian"),
                KeyboardButton(text="🇷🇺 Russian → 🇺🇿 Uzbek"),
            ],
            [
                KeyboardButton(text="🇺🇿 Uzbek → 🇬🇧 English"),
                KeyboardButton(text="🇬🇧 English → 🇺🇿 Uzbek"),
            ],
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Tarjima:\nQuyidan WebApp yoki til juftligini tanlang.",
        reply_markup=input_webapp
    )

    # Til tanlash menyusi alohida jo‘natiladi
    await message.answer("Til yo‘nalishini tanlang:", reply_markup=langs)



@dp.message()
async def all_messages(message: Message):
    user_id = message.from_user.id

    # ==== 1) WebAppdan kelgan tarjima natijasi ====
    if message.web_app_data:
        result = message.web_app_data.data
        await message.answer(f"🌐 WebApp tarjimasi:\n\n{result}")
        return

    # ==== 2) Til yo‘nalishini tanlash ====
    if "→" in message.text:
        langs = {
            "🇺🇿 Uzbek → 🇷🇺 Russian": ("uz", "ru"),
            "🇷🇺 Russian → 🇺🇿 Uzbek": ("ru", "uz"),
            "🇺🇿 Uzbek → 🇬🇧 English": ("uz", "en"),
            "🇬🇧 English → 🇺🇿 Uzbek": ("en", "uz"),
        }

        src, dest = langs[message.text]
        user_lang[user_id] = {"src": src, "dest": dest}

        await message.answer(f"Tanlandi: {message.text}\nEndi tarjima qilinadigan matnni yuboring.")
        return

    # ==== 3) Til tanlanmagan bo‘lsa → tanlashni so‘rash ====
    if user_id not in user_lang:
        await message.answer("⛔ Avval tarjima yo‘nalishini tanlang!", reply_markup=lang_menu())
        return

    src = user_lang[user_id]["src"]
    dest = user_lang[user_id]["dest"]

    # ==== 4) Oddiy matnni tarjima qilish ====
    try:
        translated = translator.translate(message.text, src=src, dest=dest)
        await message.answer(f"🔄 Tarjima:\n\n{translated.text}")
    except Exception as e:
        await message.answer(f"Xato: {e}")

@dp.message()
async def h(message: Message):
    if message.web_app_data:
        data = message.web_app_data.data  # bu string; biz JSON jo'natganmiz
        # parse JSON:
        import json
        try:
            payload = json.loads(data)
            if payload.get("type") == "webapp_translation":
                await message.answer(f"WebApp tarjimasi:\n\n{payload['text']}")
                return
        except Exception:
            # oddiy matn bo'lishi mumkin
            await message.answer(f"WebAppdan: {data}")
            return

    # boshqa oddiy xabarlar
    await message.answer("Siz: " + message.text)



# BOTNI ISHGA TUSHIRISH
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
