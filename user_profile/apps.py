import os.path
import requests
from PIL import Image

from django.apps import AppConfig


class UserProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_profile'

    verbose_name = 'Профиль пользователя'
    verbose_name_plural = 'Профили пользователей'

    def ready(self):
        profile_images = 'user_profile/static/user_profile/img/profile_images'
        default_image = 'user_profile/static/user_profile/img/default.png'
        if not os.path.exists(profile_images):
            os.mkdir(profile_images)
        if not os.path.exists(default_image):
            try:
                with open(default_image, 'wb') as img:
                    img.write(requests.get('https://upload.wikimedia.org/wikipedia/commons/'
                                           'thumb/b/bc/Unknown_person.jpg/800px-Unknown_person.jpg').content)
            except:
                Image.new('RGB', (128, 128), (0, 0, 0)).save(default_image)
