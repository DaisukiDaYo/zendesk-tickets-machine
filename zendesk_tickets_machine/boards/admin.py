from django.contrib import admin

from .models import Board, BoardGroup


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


@admin.register(BoardGroup)
class BoardGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
