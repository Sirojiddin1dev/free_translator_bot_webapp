from django.urls import path
from .views import *

urlpatterns = [
    path("paynet/", paynet_gateway),
    path("gizmo-stats/<int:user_id>/", gizmo_stats),

]