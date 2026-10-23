
from decimal import Decimal

from rest_framework import serializers

from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    class Meta:
        model = Budget
        fields = ("id", "user", "category", "amount")
        read_only_fields = ("id", "user")
        validators = []

    def validate(self, attrs):
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return attrs

        category = attrs.get(
            "category",
            self.instance.category if self.instance else None,
        )

        if category:
            existing = Budget.objects.filter(
                user=request.user,
                category=category,
            )

            if self.instance is not None:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise serializers.ValidationError({
                    "category": (
                        "A budget already exists for this category. "
                        "Update the existing budget instead."
                    )
                })

        return attrs
