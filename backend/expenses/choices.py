
from django.db import models


class ExpenseCategory(models.TextChoices):
    FOOD = "food", "Food"
    TRANSPORT = "transport", "Transport"
    RENT = "rent", "Rent"
    UTILITIES = "utilities", "Utilities"
    ENTERTAINMENT = "entertainment", "Entertainment"
    HEALTHCARE = "healthcare", "Healthcare"
    SHOPPING = "shopping", "Shopping"
    OTHER = "other", "Other"
