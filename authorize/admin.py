from django.contrib import admin
from django.utils import timezone
from django.contrib import messages

from .models import ActivatedUser, ResetPasswordCode, PreviousPassword


# Register your models here.
@admin.action(description='Активировать пользователей')
def activate_users(_, __, queryset):
    for obj in queryset:
        obj.activated = True
        obj.activated_on = timezone.now()
        obj.save()


@admin.action(description='Обновить дату активации')
def update_activated_date(_, __, queryset):
    for obj in queryset:
        obj.activated_on = timezone.now()
        obj.save()


@admin.action(description='Заблокировать навсегда')
def permanent_ban(modeladmin, request, queryset):

    MAX_BAN = 5

    if len(queryset) > MAX_BAN:
        modeladmin.message_user(request, f'Вы можете заблокировать не более {MAX_BAN} пользователей за раз',
                                messages.ERROR)
    else:
        for obj in queryset:
            obj.is_permanent_banned = True
            obj.banned_on = timezone.now()
            obj.banned_by_username = request.user.username
            obj.save()


@admin.action(description='Снять временный бан')
def unban_tempban(_, __, queryset):
    for obj in queryset:
        obj.is_banned = False
        obj.banned_on = None if not obj.is_permanent_banned else obj.banned_on
        obj.banned_until = None
        obj.banned_message = '' if not obj.is_permanent_banned else obj.banned_message
        obj.banned_by_username = '' if not obj.is_banned else obj.banned_by_username
        obj.save()


@admin.action(description='Снять перманентный бан')
def unban_permanent(_, __, queryset):
    for obj in queryset:
        obj.is_permanent_banned = False
        obj.banned_on = None if not obj.is_banned else obj.banned_on
        obj.banned_message = '' if not obj.is_banned else obj.banned_message
        obj.banned_by_username = '' if not obj.is_banned else obj.banned_by_username
        obj.save()


class UserAdmin(admin.ModelAdmin):
    pass


class ActivatedUserAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    readonly_fields = ('verification_code', 'code_valid_until',)
    list_display = ('id', 'user', 'activated', )
    list_display_links = ('id', 'user',)
    list_filter = ('activated', 'activated_on', 'is_banned', 'is_permanent_banned')
    search_fields = ('user__username', 'verification_code',)
    search_help_text = 'Логин или ключ активации'

    actions = (activate_users, update_activated_date, permanent_ban, unban_tempban, unban_permanent)


admin.site.register(ActivatedUser, ActivatedUserAdmin)
