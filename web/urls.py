from django.urls import path
from . import views

urlpatterns = [
    path("", views.webapp, name="webapp"),
    path("api/translate/", views.translate_api, name="translate_api"),
]