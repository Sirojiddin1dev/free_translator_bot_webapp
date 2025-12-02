from django.apps import AppConfig
import asyncio
from bot.bot import on_startup


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        try:
            asyncio.run(on_startup())
        except:
            pass
