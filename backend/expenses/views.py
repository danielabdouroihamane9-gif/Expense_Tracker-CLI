import csv
from decimal import Decimal
from django.http import HttpResponse

from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from budgets.models import Budget
from expenses.choices import ExpenseCategory
from expenses.models import Expense
from .serializers import ExpenseSerializer, MonthlySummaryQuerySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = {
        "category": ["exact"],
        "occurred_on": ["exact", "gte", "lte"],
        "amount": ["gte", "lte"],
    }

    search_fields = ["description"]

    ordering_fields = [
        "occurred_on",
        "amount",
        "created_at",
        "category",
    ]

    ordering = ["-occurred_on", "-created_at"]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Expense.objects.none()

        return Expense.objects.filter(user=user)

    def perform_create(self, serializer):
        user_settings = getattr(self.request.user, "settings", None)

        if user_settings is None:
            raise ValidationError({
                "detail": (
                    "Your account settings are missing. "
                    "Please contact support."
                )
            })

        serializer.save(
            user=self.request.user,
            currency=user_settings.currency,
        )
    
        
    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        query_serializer = MonthlySummaryQuerySerializer(
            data=request.query_params
        )
        query_serializer.is_valid(raise_exception=True)

        today = timezone.localdate()

        year = query_serializer.validated_data.get("year", today.year)
        month = query_serializer.validated_data.get("month", today.month)

        monthly_expenses = self.get_queryset().filter(
            occurred_on__year=year,
            occurred_on__month=month,
        )

        spending_by_category = {
            row["category"]: row["total"]
            for row in monthly_expenses
            .values("category")
            .annotate(total=Sum("amount"))
        }

        budget_by_category = dict(
            Budget.objects.filter(user=request.user)
            .values_list("category", "amount")
        )

        user_settings = getattr(request.user, "settings", None)

        categories = []
        total_spent = Decimal("0.00")

        for category, label in ExpenseCategory.choices:
            spent = spending_by_category.get(
                category, Decimal("0.00")
            )
            budget = budget_by_category.get(category)

            remaining = (
                budget - spent if budget is not None else None
            )

            percentage_used = None
            if budget is not None and budget > 0:
                percentage_used = (
                    spent / budget * Decimal("100")
                ).quantize(Decimal("0.01"))

            categories.append({
                "category": category,
                "label": label,
                "spent": spent,
                "budget": budget,
                "remaining": remaining,
                "percentage_used": percentage_used,
            })

            total_spent += spent

        return Response({
            "year": year,
            "month": month,
            "currency": (
                user_settings.currency
                if user_settings is not None
                else None
            ),
            "total_spent": total_spent,
            "categories": categories,
        })

        
    @action(detail=False, methods=["get"], url_path="export")
    def export_csv(self, request):
        # Apply the existing user-scoped queryset and API filters.
        queryset = self.filter_queryset(self.get_queryset())

        response = HttpResponse(
            content_type="text/csv; charset=utf-8"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="expenses-'
            f'{timezone.localdate().isoformat()}.csv"'
        )

        # UTF-8 BOM improves compatibility with spreadsheet software.
        response.write("\ufeff")

        writer = csv.writer(response)

        writer.writerow([
            "id",
            "occurred_on",
            "amount",
            "currency",
            "category",
            "description",
            "created_at",
        ])

        for expense in queryset.iterator():
            writer.writerow([
                str(expense.id),
                expense.occurred_on.isoformat(),
                format(expense.amount, ".2f"),
                expense.currency,
                expense.category,
                safe_csv_text(expense.description),
                expense.created_at.isoformat(),
            ])

        return response


def safe_csv_text(value):
    """Neutralize potentially executable spreadsheet formulas."""
    text = "" if value is None else str(value)

    if text.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + text

    return text
