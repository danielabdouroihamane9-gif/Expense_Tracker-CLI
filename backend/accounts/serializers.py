import re
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import UserSettings


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            *User._meta.get_field("username").validators,
            UniqueValidator(queryset=User.objects.all()),
        ],
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        default="",
    )

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    currency = serializers.CharField(
        max_length=3,
        required=False,
        default="USD",
    )

    def validate_email(self, value):
        return value.strip().lower()

    def validate_currency(self, value):
        value = value.strip().upper()

        if len(value) != 3 or not value.isalpha() or not value.isascii():
            raise serializers.ValidationError(
                "Currency must contain exactly three letters."
            )

        return value

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "The passwords do not match."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password_confirm")

        password = validated_data.pop("password")
        currency = validated_data.pop("currency")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        UserSettings.objects.create(
            user=user,
            currency=currency,
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "currency",
            "date_joined",
        )
        read_only_fields = fields

    def get_currency(self, obj):
        user_settings = getattr(obj, "settings", None)

        if user_settings is None:
            return None

        return user_settings.currency


class UserSettingsSerializer(serializers.ModelSerializer):
    currency = serializers.CharField(max_length=3)

    class Meta:
        model = UserSettings
        fields = ["currency"]

    def validate_currency(self, value):
        currency = value.strip().upper()

        if not re.fullmatch(r"[A-Z]{3}", currency, flags=re.ASCII):
            raise serializers.ValidationError(
                "Enter a valid three-letter currency code."
            )

        # Only enforce the change restriction when the value changes.
        if self.instance and currency != self.instance.currency:
            from budgets.models import Budget
            from expenses.models import Expense

            user = self.instance.user

            has_expenses = Expense.objects.filter(
                user=user
            ).exists()

            has_budgets = Budget.objects.filter(
                user=user
            ).exists()

            if has_expenses or has_budgets:
                raise serializers.ValidationError(
                    "Currency cannot be changed while expenses "
                    "or budgets exist. No currency conversion "
                    "is performed."
                )

        return currency