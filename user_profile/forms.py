from django import forms
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile

from news_django.settings import MAX_FILESIZE
from user_profile.models import ExtendedUser


class ImageForm(forms.Form):
    OK = 0
    SIZE = 1
    ERROR = 2

    file = forms.ImageField()

    def check_and_save(self, file: UploadedFile, user: User) -> int:
        if file.size > MAX_FILESIZE:
            return self.SIZE
        try:
            DEST = f'user_profile/static/user_profile/img/profile_images/{user.id}.png'
            with open(DEST, 'wb+') as img:
                for chunk in file.chunks():
                    img.write(chunk)
            return self.OK
        except Exception as e:
            return self.ERROR


class UserInfoForm(forms.Form):
    city = forms.CharField(label='Город', required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'text-hint': 'Введите город'}))
    company = forms.CharField(label='Компания', required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'text-hint': 'Название компании'}))
    website = forms.CharField(label='Сайт', required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'text-hint': 'Ваш сайт'}))
    mobile = forms.CharField(label='Телефон', required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel',
                                                           'pattern': '[+]{1}[0-9]{11,14}',
                                                           'text-hint': 'Введите номер телефона'}))

    # def from_user(self, user: ExtendedUser):
    #     self.city.initial = user.city
    #     self.company.initial = user.company
    #     self.website.initial = user.websites
    #     self.mobile.initial = user.mobile
