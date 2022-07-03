from django.contrib import admin, messages
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from django.http import HttpResponseRedirect as redirect
from django.shortcuts import render
from django.contrib.auth.hashers import make_password

from .models import ActivatedUser, ResetPasswordCode, PreviousPassword
from .forms import TempbanAdminForm, PasswordChangeAdminForm, BanAdminForm
from .checks import LoginAbility, PasswordStrongCheck


# Register your models here.
@admin.action(description='Активировать пользователей')
def activate_users(_, __, queryset):
    for obj in queryset:
        obj.activated = True
        obj.activated_on = timezone.now()
        obj.save()


@admin.action(description='Деактивировать пользователей')
def deactivate_users(_, __, queryset):
    for obj in queryset:
        obj.activated = False
        obj.activated_on = None
        obj.save()


@admin.action(description='Обновить дату активации')
def update_activated_date(_, __, queryset):
    for obj in queryset:
        obj.activated_on = timezone.now()
        obj.save()


@admin.action(description='Заблокировать на время')
def tempban(modeladmin, request, queryset):
    MAX_BAN = 5
    if len(queryset) > MAX_BAN:
        modeladmin.message_user(request, f'Вы не можете заблокировать больше {MAX_BAN} пользователей за раз',
                                messages.ERROR)
        return redirect(request.get_full_path())

    form = None
    if 'post' in request.POST:
        form = TempbanAdminForm(request.POST)
        if form.is_valid():
            until = form.cleaned_data.get('until')
            message = form.cleaned_data.get('message')
            if until < timezone.now():
                modeladmin.message_user(request, 'Дата не может быть меньше текущего времени',
                                        messages.ERROR)
            else:
                for obj in queryset:
                    obj.is_banned = True
                    obj.banned_on = timezone.now()
                    obj.banned_until = until
                    obj.banned_message = message if message else ''
                    obj.banned_by_username = request.user.username
                    LoginAbility.logout_user(obj.user)
                    obj.save()
                modeladmin.message_user(request, f'Пользователи заблокированны до {until}')
                return redirect(request.get_full_path())
    if not form:
        form = TempbanAdminForm()
    context = {
        'form': form,
        'items': queryset
    }
    return render(request, 'authorize/admin/admin_tempban.html', context=context)


@admin.action(description='Заблокировать навсегда')
def permanent_ban(modeladmin, request, queryset):
    MAX_BAN = 5
    if len(queryset) > MAX_BAN:
        modeladmin.message_user(request, f'Вы можете заблокировать не более {MAX_BAN} пользователей за раз',
                                messages.ERROR)
        return redirect(request.get_full_path())
    form = None
    if 'post' in request.POST:
        form = BanAdminForm(request.POST)
        if form.is_valid():
            for obj in queryset:
                obj.is_permanent_banned = True
                obj.banned_on = timezone.now()
                obj.banned_by_username = request.user.username
                msg = form.cleaned_data.get('message')
                if msg:
                    obj.banned_message = msg
                LoginAbility.logout_user(obj.user)
                obj.save()
            _f = 'пользователю' if len(queryset) == 1 else 'пользователям'
            modeladmin.message_user(request, f'Блокировка применена к {len(queryset)} {_f}')
            return redirect(request.get_full_path())
    if not form:
        form = BanAdminForm()
    context = {
        'form': form,
        'items': queryset,
    }
    return render(request, 'authorize/admin/admin_permban.html', context=context)


@admin.action(description='Снять временный бан')
def unban_tempban(_, __, queryset):
    for obj in queryset:
        obj.is_banned = False
        obj.banned_until = None
        if not obj.is_permanent_banned:
            obj.banned_on = None
            obj.banned_message = ''
            obj.banned_by_username = ''
        obj.save()


@admin.action(description='Снять перманентный бан')
def unban_permanent(_, __, queryset):
    for obj in queryset:
        obj.is_permanent_banned = False
        if not obj.is_banned:
            obj.banned_on = None
            obj.banned_message = ''
            obj.banned_by_username = ''
        obj.save()


@admin.action(description='Сменить пароль')
def change_password(modeladmin, request, queryset):
    MAX_ACTION = 3
    if len(queryset) > MAX_ACTION:
        modeladmin.message_user(request, f'Вы можете сменить пароль не более {MAX_ACTION} пользователей за раз',
                                messages.ERROR)
    form = None
    if 'post' in request.POST:
        form = PasswordChangeAdminForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('pass1') != form.cleaned_data.get('pass2'):
                modeladmin.message_user(request, 'Пароли должны совпадать', messages.ERROR)
            else:
                pass1 = form.cleaned_data.get('pass1')
                if PasswordStrongCheck.password_test(request, pass1, is_admin_messages=True, modeladmin=modeladmin):
                    for obj in queryset:
                        PreviousPassword.objects.create(
                            user=obj.user,
                            password=obj.user.password,
                        )
                        obj.user.password = make_password(pass1)
                        obj.user.save()
                        modeladmin.message_user(request, f'Пароль успешно изменен {len(queryset)} '
                                                         f'{"пользователю" if len(queryset) == 1 else "пользователям"}')
                        return redirect(request.get_full_path())
    if not form:
        form = PasswordChangeAdminForm()
    context = {
        'form': form,
        'items': queryset,
    }
    return render(request, 'authorize/admin/admin_change_password.html', context=context)


class UserAdmin(admin.ModelAdmin):

    def nothing(self, request, queryset):
        pass

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    actions = [nothing]


class ActivatedUserAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    readonly_fields = ('verification_code', 'code_valid_until', 'activated_on',)
    list_display = ('id', 'user', 'activated', 'is_banned', 'is_permanent_banned')
    list_display_links = ('id', 'user',)
    list_filter = ('activated', 'activated_on', 'is_banned', 'is_permanent_banned')
    search_fields = ('user__username', 'verification_code',)
    search_help_text = 'Логин или ключ активации'

    actions = (activate_users, deactivate_users, update_activated_date, change_password,
               tempban, permanent_ban, unban_tempban, unban_permanent)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ActivatedUser, ActivatedUserAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Permission)
