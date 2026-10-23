import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.http import HttpResponse
from django.db import transaction

from django.db.models import Sum, Avg, Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from budgets.models import Budget
from expenses.choices import ExpenseCategory
from expenses.models import Expense
from .serializers import ExpenseSerializer, MonthlySummaryQuerySerializer, ExpenseDuplicateSerializer
from accounts.models import UserSettings

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

    @action(
        detail=False,
        methods=["post"],
        url_path="import",
        parser_classes=[MultiPartParser, FormParser],
    )
    def import_csv(self, request):
        uploaded_file = request.FILES.get("file")

        if uploaded_file is None:
            return Response(
                {
                    "detail": (
                        "Upload a CSV file using the "
                        "form-data field named 'file'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not uploaded_file.name.lower().endswith(".csv"):
            return Response(
                {"detail": "File must have a .csv extension."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Obtain the authenticated user's configured currency.
        try:
            current_currency = request.user.settings.currency
        except UserSettings.DoesNotExist:
            return Response(
                {"detail": "User currency settings were not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rows, row_errors, file_error = parse_expense_csv(
            uploaded_file,
            current_currency,
        )

        if file_error:
            return Response(
                {"detail": file_error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reject the entire file if even one row is invalid.
        # No database writes have happened yet.
        if row_errors:
            return Response(
                {
                    "detail": (
                        "CSV import rejected. "
                        "No expenses were created."
                    ),
                    "errors": row_errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        imported = 0
        skipped_duplicates = 0

        # Keep duplicate checks and inserts in one transaction.
        with transaction.atomic():
            existing_keys = set(
                Expense.objects.filter(
                    user=request.user
                ).values_list(
                    "occurred_on",
                    "amount",
                    "category",
                    "description",
                    "currency",
                )
            )

            for row in rows:
                duplicate_key = (
                    row["occurred_on"],
                    row["amount"],
                    row["category"],
                    row["description"],
                    row["currency"],
                )

                # Match the duplicate rule used by the CLI.
                if duplicate_key in existing_keys:
                    skipped_duplicates += 1
                    continue

                Expense.objects.create(
                    user=request.user,
                    **row,
                )

                # Also catches duplicate rows within this file.
                existing_keys.add(duplicate_key)
                imported += 1

        return Response(
            {
                "detail": "CSV import completed.",
                "rows_processed": len(rows),
                "imported": imported,
                "skipped_duplicates": skipped_duplicates,
            },
            status=status.HTTP_200_OK,
        )


    @action(
        detail=True,
        methods=["post"],
        url_path="duplicate",
    )
    def duplicate(self, request, pk=None):
        source = self.get_object()

        input_serializer = ExpenseDuplicateSerializer(
            data=request.data
        )
        input_serializer.is_valid(raise_exception=True)

        duplicate = Expense.objects.create(
            user=request.user,
            occurred_on=input_serializer.validated_data["occurred_on"],
            amount=source.amount,
            currency=source.currency,
            category=source.category,
            description=source.description,
        )

        output_serializer = ExpenseSerializer(
            duplicate,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="statistics",
    )
    def statistics(self, request):
        # get_queryset() already restricts records to the current user.
        # Existing API filters are applied to the report as well.
        queryset = self.filter_queryset(self.get_queryset())

        aggregates = queryset.aggregate(
            count=Count("id"),
            total=Sum("amount"),
            average=Avg("amount"),
        )

        total = (
            aggregates["total"] or Decimal("0.00")
        ).quantize(Decimal("0.01"))

        average = (
            aggregates["average"] or Decimal("0.00")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        highest = queryset.order_by(
            "-amount",
            "-occurred_on",
            "id",
        ).first()

        lowest = queryset.order_by(
            "amount",
            "occurred_on",
            "id",
        ).first()

        category_rows = queryset.values(
            "category"
        ).annotate(
            total=Sum("amount"),
            count=Count("id"),
        ).order_by(
            "-total",
            "category",
        )

        spending_by_category = [
            {
                "category": row["category"],
                "total": row["total"],
                "count": row["count"],
            }
            for row in category_rows
        ]

        context = self.get_serializer_context()

        return Response({
            "count": aggregates["count"],
            "total_spending": total,
            "average_expense": average,
            "highest_expense": (
                ExpenseSerializer(
                    highest,
                    context=context,
                ).data
                if highest else None
            ),
            "lowest_expense": (
                ExpenseSerializer(
                    lowest,
                    context=context,
                ).data
                if lowest else None
            ),
            "spending_by_category": spending_by_category,
            "top_categories": spending_by_category[:5],
        })

def safe_csv_text(value):
    """Neutralize potentially executable spreadsheet formulas."""
    text = "" if value is None else str(value)

    if text.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + text

    return text


def parse_expense_csv(uploaded_file, default_currency):
    """
    Parse and validate an expense CSV file.

    Accepts the legacy CLI format:
        Date,Amount,Category,Description

    Currency is optional in that format.

    Also accepts the Django export format:
        id,occurred_on,amount,currency,category,
        description,created_at

    The id and created_at columns are ignored during import.
    """
    try:
        content = uploaded_file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], [], "CSV file must use UTF-8 encoding."

    try:
        reader = csv.DictReader(
            io.StringIO(content, newline=""),
            restkey="__extra_fields__",
            strict=True,
        )

        raw_headers = reader.fieldnames

        if not raw_headers:
            return [], [], "CSV file must contain a header row."

        headers = [
            str(header or "").strip().lower()
            for header in raw_headers
        ]

        if any(not header for header in headers):
            return [], [], "CSV contains an empty column name."

        if len(headers) != len(set(headers)):
            return [], [], "CSV contains duplicate column names."

        header_set = set(headers)

        if "date" in header_set and "occurred_on" in header_set:
            return (
                [],
                [],
                "Use either 'Date' or 'occurred_on', not both.",
            )

        date_header = (
            "occurred_on"
            if "occurred_on" in header_set
            else "date"
        )

        required_headers = {
            date_header,
            "amount",
            "category",
            "description",
        }

        missing_headers = required_headers - header_set

        if missing_headers:
            missing = ", ".join(sorted(missing_headers))
            return [], [], f"Missing required columns: {missing}."

        allowed_headers = {
            "date",
            "occurred_on",
            "amount",
            "currency",
            "category",
            "description",
            "id",
            "created_at",
        }

        unknown_headers = header_set - allowed_headers

        if unknown_headers:
            unknown = ", ".join(sorted(unknown_headers))
            return [], [], f"Unsupported CSV columns: {unknown}."

        parsed_rows = []
        row_errors = []

        for row_number, raw_row in enumerate(reader, start=2):
            extra_fields = raw_row.get("__extra_fields__")

            raw_values = [
                raw_row.get(header)
                for header in raw_headers
            ]

            # Ignore completely blank rows.
            if (
                not any(
                    value is not None and str(value).strip()
                    for value in raw_values
                )
                and not extra_fields
            ):
                continue

            row = {
                normalized: raw_row.get(original)
                for original, normalized in zip(
                    raw_headers, headers
                )
            }

            errors = {}

            if extra_fields:
                errors["columns"] = [
                    "Row contains more values than the header."
                ]

            # Validate the date format strictly as YYYY-MM-DD.
            date_text = str(row.get(date_header) or "").strip()

            try:
                parsed_date = date.fromisoformat(date_text)

                if parsed_date.isoformat() != date_text:
                    raise ValueError

            except ValueError:
                errors["occurred_on"] = [
                    "Enter a valid date in YYYY-MM-DD format."
                ]

            # Normalize monetary values to two decimal places,
            # using the same ROUND_HALF_UP rule as the CLI.
            raw_amount = row.get("amount")
            amount_text = str(raw_amount or "").strip()

            try:
                amount_value = Decimal(amount_text)

                if (
                    not amount_value.is_finite()
                    or amount_value <= 0
                ):
                    raise ValueError

                amount_value = amount_value.quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )

                if amount_value <= 0:
                    raise ValueError

                amount_text = format(amount_value, ".2f")

            except (InvalidOperation, ValueError):
                errors["amount"] = [
                    "Enter a valid positive amount."
                ]

            # Currency is optional in legacy CLI files.
            # If supplied, it must match the user's currency.
            currency = default_currency

            if "currency" in header_set:
                currency_text = str(
                    row.get("currency") or ""
                ).strip().upper()

                if not currency_text:
                    errors["currency"] = [
                        "Currency cannot be blank."
                    ]
                elif not (
                    len(currency_text) == 3
                    and currency_text.isascii()
                    and currency_text.isalpha()
                ):
                    errors["currency"] = [
                        "Enter a three-letter currency code."
                    ]
                elif currency_text != default_currency:
                    errors["currency"] = [
                        f"Currency must match your account currency "
                        f"({default_currency}). No conversion is performed."
                    ]
                else:
                    currency = currency_text

            # Normalize the category to match the CLI behavior.
            payload = {
                "occurred_on": date_text,
                "amount": amount_text,
                "category": str(
                    row.get("category") or ""
                ).strip().lower(),
                "description": row.get("description"),
            }

            # Reuse the existing API serializer's validation rules.
            serializer = ExpenseSerializer(data=payload)
            serializer.is_valid()

            for field, messages in serializer.errors.items():
                # Keep our more specific date/amount errors.
                if field not in errors:
                    errors[field] = [
                        str(message) for message in messages
                    ]

            if errors:
                row_errors.append({
                    "row": row_number,
                    "errors": errors,
                })
                continue

            validated = serializer.validated_data

            parsed_rows.append({
                "occurred_on": validated["occurred_on"],
                "amount": validated["amount"],
                "category": validated["category"],
                "description": validated["description"],
                "currency": currency,
            })

        if not parsed_rows and not row_errors:
            return [], [], "CSV file contains no data rows."

        return parsed_rows, row_errors, None

    except csv.Error as error:
        return [], [], f"Invalid CSV structure: {error}"