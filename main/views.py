import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


USERNAME = "cloudplay_test"
PASSWORD = "x7G9asJH2"


def check_auth(request):
    auth = request.headers.get("Authorization")
    if not auth:
        return False

    try:
        method, encoded = auth.split(" ")
        decoded = base64.b64decode(encoded).decode()
        user, pwd = decoded.split(":")
        return user == USERNAME and pwd == PASSWORD
    except:
        return False


@csrf_exempt
def paynet_gateway(request):
    if not check_auth(request):
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    # ❗ Faqat POST bo'lishi kerak
    if request.method != "POST":
        return JsonResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32300, "message": "POST required"},
            "id": None
        })

    body = json.loads(request.body)

    method = body.get("method")
    req_id = body.get("id")

    if method == "GetInformation":
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "status": 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fields": {
                    "name": "Test User",
                    "balance": 500000
                }
            }
        })

    if method == "PerformTransaction":
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "providerTrnId": 123456,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fields": {}
            }
        })

    if method == "CheckTransaction":
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "providerTrnId": 123456,
                "transactionState": 1,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })

    if method == "CancelTransaction":
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "providerTrnId": 123456,
                "transactionState": 2,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })

    if method == "GetStatement":
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "statements": []
            }
        })

    return JsonResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": "Method not found"}
    })
from django.http import JsonResponse
from .gizmo import (
    gizmo_get_sessions,
    get_total_played,
    get_today_played,
    get_played_between,
    get_month_played
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse

def safe_sessions(sessions):
    if isinstance(sessions, str):
        try:
            sessions = json.loads(sessions)
        except json.JSONDecodeError:
            sessions = []
    return sessions

# Query parameters swagger uchun
from_param = openapi.Parameter(
    'from', openapi.IN_QUERY,
    description="Boshlanish sanasi (YYYY-MM-DD format)",
    type=openapi.TYPE_STRING,
    required=False
)

to_param = openapi.Parameter(
    'to', openapi.IN_QUERY,
    description="Tugash sanasi (YYYY-MM-DD format)",
    type=openapi.TYPE_STRING,
    required=False
)

year_param = openapi.Parameter(
    'year', openapi.IN_QUERY,
    description="Oylik statistikani olish uchun yil (YYYY)",
    type=openapi.TYPE_INTEGER,
    required=False
)

month_param = openapi.Parameter(
    'month', openapi.IN_QUERY,
    description="Oylik statistikani olish uchun oy (1-12)",
    type=openapi.TYPE_INTEGER,
    required=False
)

@swagger_auto_schema(
    method='get',
    manual_parameters=[from_param, to_param, year_param, month_param],
    operation_description="Foydalanuvchi o'yin statistikasi",
    responses={200: openapi.Response(
        description="Statistika natijalari",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'total_seconds': openapi.Schema(type=openapi.TYPE_INTEGER, description='Umumiy o‘yin vaqti (soniyalar)'),
                'today_seconds': openapi.Schema(type=openapi.TYPE_INTEGER, description='Bugungi o‘yin vaqti (soniyalar)'),
                'between_seconds': openapi.Schema(type=openapi.TYPE_INTEGER, description='Berilgan davrdagi o‘yin vaqti (soniyalar)', nullable=True),
                'month_seconds': openapi.Schema(type=openapi.TYPE_INTEGER, description='Berilgan oy va yil uchun o‘yin vaqti (soniyalar)', nullable=True),
            }
        )
    )}
)
@api_view(['GET'])
def gizmo_stats(request, user_id):
    all_sessions = gizmo_get_sessions()
    # userId bo'yicha filtr
    if all_sessions:
        print("ishladi")
    sessions = [s for s in all_sessions if s.get("userId") == user_id]
    limit = None
    if get_today_played(sessions)/3600 >= 8:
        limit = "kunlik limit tugadi"

    result = {
        "total_seconds": get_total_played(sessions),
        "today_seconds": get_today_played(sessions),
        "between_seconds": None,
        "month_seconds": None,
        "limit": limit,
    }

    # period
    f = request.GET.get("from")
    t = request.GET.get("to")
    if f and t:
        result["between_seconds"] = get_played_between(sessions, f, t)

    # month stats
    year = request.GET.get("year")
    month = request.GET.get("month")
    if year and month:
        result["month_seconds"] = get_month_played(
            sessions,
            int(year),
            int(month)
        )

    return JsonResponse(result)