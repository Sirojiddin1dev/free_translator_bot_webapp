from django.http import JsonResponse
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import requests
from django.conf import settings
import json

def gizmo_get_sessions():
    url = f"{settings.GIZMO_BASE_URL}/usersessions"
    try:
        r = requests.get(
            url,
            params={},  # hech narsa yubormaymiz
            auth=HTTPBasicAuth(settings.GIZMO_LOGIN, settings.GIZMO_PASSWORD),
            timeout=10
        )
        print("HTTP status code:", r.status_code)
        print("Raw response text:", r.text[:500])
    except Exception as e:
        print("Requests error:", e)
        return []

    # JSON parse
    try:
        data = r.json()
        print("Parsed JSON type:", type(data))
        if isinstance(data, dict):
            if "result" in data:
                sessions = data["result"]
                print("Sessions count:", len(sessions))
                return sessions if isinstance(sessions, list) else []
            else:
                print("No 'result' key in JSON:", data.keys())
                return []
        elif isinstance(data, list):
            return data
        else:
            return []
    except Exception as e:
        print("JSON decode error:", e)
        return []


def parse_dt(s):
    if s is None:
        return None
    return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")

def get_total_played(sessions):
    return sum(s.get("span", 0) for s in sessions)

def get_today_played(sessions):
    today = datetime.now().date()
    total = 0
    for s in sessions:
        created = parse_dt(s["createdTime"])
        if created and created.date() == today:
            total += s.get("span", 0)
    return total

def get_played_between(sessions, from_date, to_date):
    from_date_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_date_dt = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    total = 0
    for s in sessions:
        start = parse_dt(s["createdTime"])
        end = parse_dt(s["endTime"]) or datetime.now()
        if start and start >= from_date_dt and end <= to_date_dt:
            total += s.get("span", 0)
    return total

def get_month_played(sessions, year, month):
    total = 0
    for s in sessions:
        start = parse_dt(s["createdTime"])
        if start and start.year == year and start.month == month:
            total += s.get("span", 0)
    return total