
from django.contrib import admin

from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "amount")
    list_filter = ("category",)
    search_fields = ("user__username", "user__email")
    list_select_related = ("user",)
