import os.path

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import ObjectDoesNotExist
from django.contrib import messages
from django.http import HttpResponseRedirect as redirect
from django.http import HttpResponse

from .models import ExtendedUser
from .forms import ImageForm, UserInfoForm, ChangePasswordForm, MAX_FILESIZE


def has_image(r):
    return os.path.exists(f'user_profile/static/user_profile/img/profile_images/{r.user.id}.png')


def get_extended_user(user):
    try:
        e_user = ExtendedUser.objects.get(user_id=user.id)
    except ObjectDoesNotExist:
        e_user = ExtendedUser.objects.create(user=user)
    return e_user


# Create your views here.
@login_required
def def_profile(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            code = form.check_and_save(request.FILES.get('file'), request.user)
            if code == form.OK:
                messages.success(request, 'Фотография обновлена')
            elif code == form.SIZE:
                messages.error(request, f'Максимальный размер файла: {int(MAX_FILESIZE / 1024 / 1024)} МБ')
            elif code == form.ERROR:
                messages.error(request, 'Ошибка сохранения. Возможно файл поврежден или не поддерживатеся.')
    else:
        form = ImageForm()
    e_user = get_extended_user(request.user)
    data = {
        'has_image': has_image(request),
        'e_user': e_user,
        'form': form,
    }
    return render(request, 'user_profile/profile.html', context=data)


@login_required
def profile_user_info(request):
    e_user = get_extended_user(request.user)
    if request.method == 'POST':
        form = UserInfoForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            e_user.city = form_data.get('city')
            e_user.company = form_data.get('company')
            e_user.websites = form_data.get('website')
            e_user.mobile = form_data.get('mobile')
            e_user.save()
            messages.success(request, 'Изменения успешно сохранены')
    else:
        form = UserInfoForm(initial={
            'city': e_user.city,
            'company': e_user.company,
            'website': e_user.websites,
            'mobile': e_user.mobile,
        })
    data = {
        'has_image': has_image(request),
        'e_user': e_user,
        'form': form,
    }
    return render(request, 'user_profile/profile_edit.html', context=data)


@login_required
def profile_user_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            code = form.check(user)
            if code == ChangePasswordForm.OK:
                form.set(request.user)
                messages.success(request, 'Пароль изменен')
                login(request, user)
                return redirect('/profile/change_password')
            elif code == ChangePasswordForm.OLD:
                messages.error(request, 'Неправильный пароль')
            elif code == ChangePasswordForm.SAME:
                messages.error(request, 'Пароль не может совпадать с текущим')
            elif code == ChangePasswordForm.NOT_EQUALS:
                messages.error(request, 'Пароли не совпадают')
            elif code == ChangePasswordForm.STRONG:
                messages.error(request, 'В новом пароле должна быть хотя бы 1 заглавная и строчная буква, и 1 цифра')
            elif code == ChangePasswordForm.SYMBOLS:
                messages.error(request, 'Пароль может содержать только буквы латинского алфавита и символы $%#_-+=!@')
            elif code == ChangePasswordForm.MIN_MAX:
                messages.error(request, f'Пароль должен быть от {ChangePasswordForm.PASS_MIN} '
                                        f'до {ChangePasswordForm.PASS_MAX} символов')
            elif code == ChangePasswordForm.LOG_PASS:
                messages.error(request, 'Пароль не может совпадать с логином')
    else:
        form = ChangePasswordForm()
    data = {
        'has_image': has_image(request),
        'form': form,
    }
    return render(request, 'user_profile/profile_password.html', context=data)
