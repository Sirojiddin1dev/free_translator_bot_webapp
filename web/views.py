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
