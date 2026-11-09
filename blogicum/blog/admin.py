"""Админ-зона приложения blog."""
from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Управление категориями."""

    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Управление географическими метками."""

    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Управление публикациями."""

    list_display = (
        'title', 'author', 'category', 'location',
        'pub_date', 'is_published',
    )
    list_editable = ('is_published', 'category', 'location')
    search_fields = ('title',)
    list_filter = ('is_published', 'category', 'pub_date')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Управление комментариями."""

    list_display = ('pk', 'post', 'author', 'created_at')
    search_fields = ('text',)
