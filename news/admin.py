from django.contrib import admin
from .models import *


# Register your models here.
class TagAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('title',)
    list_display_links = ('title',)
    search_fields = ('id', 'title')
    search_help_text = 'ID или название'


class PostAdmin(admin.ModelAdmin):
    ordering = ('-creation_date', 'title')
    list_display = ('id', 'title', 'author', 'creation_date', 'is_posted')
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title', 'author__username')
    search_help_text = 'ID, название или никнейм автора'
    list_filter = ('creation_date', 'is_posted')
    readonly_fields = ('creation_date',)

    def has_add_permission(self, request):
        return False


admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
