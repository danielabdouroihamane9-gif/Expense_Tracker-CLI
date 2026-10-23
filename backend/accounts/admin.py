
from django.contrib import admin

from .models import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "currency")
    search_fields = ("user__username", "user__email")
    list_select_related = ("user",)
