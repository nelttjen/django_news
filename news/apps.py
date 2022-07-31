import os

from django.apps import AppConfig
from django.core.signals import request_finished
from django.dispatch import receiver, Signal


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    user_signal = Signal()

    def ready(self):
        if not os.path.exists('uploads'):
            os.mkdir('uploads')

        @receiver(self.user_signal)
        def update_user_activity(sender, **kwargs):
            print(sender.get_response())


