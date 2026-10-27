
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import Expense
from .choices import ExpenseCategory


def validate_expense_occurred_on(value):
    if value > timezone.localdate():
        raise serializers.ValidationError(
            "Date cannot be in the future."
        )
    return value


class ExpenseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    currency = serializers.CharField(read_only=True)

    occurred_on = serializers.DateField()

    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    category = serializers.ChoiceField(
        choices=ExpenseCategory.choices,
    )

    description = serializers.CharField(
        max_length=500,
        trim_whitespace=True,
        allow_blank=False,
    )

    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Expense
        fields = (
            "id",
            "user",
            "occurred_on",
            "amount",
            "currency",
            "category",
            "description",
            "created_at",
        )
        read_only_fields = (
            "id",
            "user",
            "currency",
            "created_at",
        )

    def to_internal_value(self, data):
        protected_fields = {
            "id",
            "user",
            "currency",
            "created_at",
        }

        supplied_fields = protected_fields.intersection(data.keys())

        if supplied_fields:
            raise serializers.ValidationError({
                field: "This field is read-only."
                for field in sorted(supplied_fields)
            })

        return super().to_internal_value(data)

    def validate_occurred_on(self, value):
        return validate_expense_occurred_on(value)


class MonthlySummaryQuerySerializer(serializers.Serializer):
    year = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=9999,
    )
    month = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=12,
    )

    def validate(self, attrs):
        has_year = "year" in attrs
        has_month = "month" in attrs

        if has_year != has_month:
            raise serializers.ValidationError(
                "Provide both 'year' and 'month', "
                "or omit both to use the current month."
            )

        return attrs


class ExpenseDuplicateSerializer(serializers.Serializer):
    occurred_on = serializers.DateField()

    def validate_occurred_on(self, value):
        return validate_expense_occurred_on(value)