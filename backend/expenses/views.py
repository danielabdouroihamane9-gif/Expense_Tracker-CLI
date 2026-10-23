
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Expense
from .serializers import ExpenseSerializer


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
