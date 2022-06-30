from django.contrib import admin
from .models import *


# Register your models here.
class TagsAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title')
    search_help_text = 'ID или название'


admin.site.register(Tag, TagsAdmin)