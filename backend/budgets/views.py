
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .models import Budget
from .serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = ["category"]
    ordering_fields = ["category", "amount"]
    ordering = ["category"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Budget.objects.none()

        return Budget.objects.filter(
            user=self.request.user
        ).order_by("category")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
