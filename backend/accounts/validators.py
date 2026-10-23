
import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


currency_code_validator = RegexValidator(
    regex=r"\A[A-Za-z]{3}\Z",
    message="Currency must be a three-letter code, such as USD or MYR.",
)


def normalize_currency_code(value):
    """Normalize a currency code and reject invalid formats."""
    if not isinstance(value, str):
        raise ValidationError("Currency must be a three-letter code.")

    normalized = value.strip().upper()

    if not re.fullmatch(r"[A-Z]{3}", normalized):
        raise ValidationError(
            "Currency must contain exactly three letters."
        )

    return normalized
