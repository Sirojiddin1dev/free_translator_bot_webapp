from django.shortcuts import render
from django.http import JsonResponse
from googletrans import Translator

translator = Translator()


def webapp(request):
    """
    WebApp HTML sahifasini qaytaradi
    """
    return render(request, "index.html")


def translate_api(request):
    """
    GET params:
      text - matn
      src  - source language code (yoki 'auto')
      dest - dest language code
    returns: {"translated": "...", "detected_lang": "..."}
    """
    text = request.GET.get("text", "")
    src = request.GET.get("src", "auto")
    dest = request.GET.get("dest", "uz")

    if not text:
        return JsonResponse({"error": "No text provided"}, status=400)

    try:
        result = translator.translate(text, src=src, dest=dest)
        return JsonResponse({
            "translated": result.text,
            "detected_lang": getattr(result, "src", src)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from bot.bot import process_update

@method_decorator(csrf_exempt, name='dispatch')
async def telegram_webhook(request):

    if request.method == "POST":
        body = json.loads(request.body.decode("utf-8"))

        # Aiogram update accept
        await process_update(body)

        return JsonResponse({"ok": True})

    return JsonResponse({"error": "GET not allowed"}, status=405)