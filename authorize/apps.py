from django.apps import AppConfig
from django.template.defaultfilters import register


class AuthorizeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authorize'
    verbose_name = 'Авторизация сайта'


@register.filter
def has_user(itemset, user):
    return itemset.filter(user=user)