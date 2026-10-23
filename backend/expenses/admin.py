
from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "occurred_on",
        "amount",
        "currency",
        "category",
        "description",
        "created_at",
    )
    list_filter = ("category", "currency", "occurred_on")
    search_fields = (
        "description",
        "user__username",
        "user__email",
    )
    readonly_fields = ("id", "created_at")
    list_select_related = ("user",)
