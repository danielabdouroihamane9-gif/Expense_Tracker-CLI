import csv
import io
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

from accounts.models import UserSettings
from expenses.models import Expense
from budgets.models import Budget

User = get_user_model()


class ExpenseAPITests(APITestCase):
    url = "/api/v1/expenses/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="expenseapiuser",
            password="Strong-Password-928!",
        )
        UserSettings.objects.create(
            user=self.user,
            currency="USD",
        )

        self.client.force_authenticate(user=self.user)

    def make_expense(self, user=None, **overrides):
        values = {
            "user": user or self.user,
            "occurred_on": date(2026, 10, 23),
            "amount": Decimal("12.30"),
            "currency": "USD",
            "category": "food",
            "description": "Lunch",
        }
        values.update(overrides)

        return Expense.objects.create(**values)

    def test_create_expense(self):
        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "12.30",
                "category": "food",
                "description": "Lunch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["amount"], "12.30")
        self.assertEqual(response.data["currency"], "USD")
        self.assertEqual(response.data["user"], self.user.pk)
        self.assertEqual(Expense.objects.count(), 1)

    def test_expense_uses_users_configured_currency(self):
        settings = self.user.settings
        settings.currency = "MYR"
        settings.save()

        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "12.30",
                "category": "food",
                "description": "Lunch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["currency"], "MYR")

    def test_client_cannot_choose_owner_or_currency(self):
        other_user = User.objects.create_user(
            username="otherexpenseuser",
            password="Strong-Password-928!",
        )
        UserSettings.objects.create(user=other_user, currency="MYR")

        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "12.30",
                "category": "food",
                "description": "Lunch",
                "user": other_user.pk,
                "currency": "MYR",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Expense.objects.count(), 0)

    def test_list_contains_only_current_users_expenses(self):
        own_expense = self.make_expense()

        other_user = User.objects.create_user(
            username="anotheruser",
            password="Strong-Password-928!",
        )
        UserSettings.objects.create(user=other_user, currency="USD")

        self.make_expense(
            user=other_user,
            description="Private expense",
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {
            item["id"] for item in response.data["results"]
        }

        self.assertEqual(returned_ids, {str(own_expense.id)})

    def test_cannot_retrieve_another_users_expense(self):
        other_user = User.objects.create_user(
            username="privateuser",
            password="Strong-Password-928!",
        )
        UserSettings.objects.create(user=other_user, currency="USD")

        other_expense = self.make_expense(user=other_user)

        response = self.client.get(
            f"{self.url}{other_expense.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_updates_own_expense(self):
        expense = self.make_expense()

        response = self.client.patch(
            f"{self.url}{expense.id}/",
            {"description": "Updated lunch"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expense.refresh_from_db()
        self.assertEqual(expense.description, "Updated lunch")

    def test_delete_own_expense(self):
        expense = self.make_expense()

        response = self.client.delete(
            f"{self.url}{expense.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())

    def test_zero_amount_is_rejected_by_api(self):
        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "0.00",
                "category": "food",
                "description": "Lunch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_category_is_rejected_by_api(self):
        response = self.client.post(
            self.url,
            {
                "occurred_on": "2026-10-23",
                "amount": "12.30",
                "category": "invalid",
                "description": "Lunch",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_category(self):
        self.make_expense(category="food")
        self.make_expense(
            category="transport",
            description="Bus ticket",
        )

        response = self.client.get(
            self.url,
            {"category": "food"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["category"], "food")

    def test_expense_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ExpenseMonthlySummaryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="summary_user",
            password="TestPassword123!",
        )
        UserSettings.objects.create(
            user=self.user,
            currency="USD",
        )

        self.other_user = User.objects.create_user(
            username="other_summary_user",
            password="TestPassword123!",
        )
        UserSettings.objects.create(
            user=self.other_user,
            currency="USD",
        )

        self.today = timezone.localdate()
        self.client.force_authenticate(user=self.user)

    def test_summary_counts_current_month_and_own_expenses(self):
        Expense.objects.create(
            user=self.user,
            occurred_on=self.today,
            amount=Decimal("12.50"),
            currency="USD",
            category="food",
            description="Lunch",
        )

        Expense.objects.create(
            user=self.user,
            occurred_on=self.today,
            amount=Decimal("7.50"),
            currency="USD",
            category="food",
            description="Dinner",
        )

        Expense.objects.create(
            user=self.user,
            occurred_on=self.today,
            amount=Decimal("5.00"),
            currency="USD",
            category="transport",
            description="Bus fare",
        )

        previous_month_date = (
            self.today.replace(day=1) - timedelta(days=1)
        )

        Expense.objects.create(
            user=self.user,
            occurred_on=previous_month_date,
            amount=Decimal("999.00"),
            currency="USD",
            category="food",
            description="Previous month expense",
        )

        Expense.objects.create(
            user=self.other_user,
            occurred_on=self.today,
            amount=Decimal("500.00"),
            currency="USD",
            category="food",
            description="Another user's expense",
        )

        Budget.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("30.00"),
        )

        Budget.objects.create(
            user=self.user,
            category="transport",
            amount=Decimal("10.00"),
        )

        response = self.client.get(
            "/api/v1/expenses/summary/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["currency"], "USD")

        self.assertEqual(
            Decimal(str(response.data["total_spent"])),
            Decimal("25.00"),
        )

        categories = {
            item["category"]: item
            for item in response.data["categories"]
        }

        food = categories["food"]
        self.assertEqual(
            Decimal(str(food["spent"])),
            Decimal("20.00"),
        )
        self.assertEqual(
            Decimal(str(food["budget"])),
            Decimal("30.00"),
        )
        self.assertEqual(
            Decimal(str(food["remaining"])),
            Decimal("10.00"),
        )
        self.assertEqual(
            Decimal(str(food["percentage_used"])),
            Decimal("66.67"),
        )

        transport = categories["transport"]
        self.assertEqual(
            Decimal(str(transport["spent"])),
            Decimal("5.00"),
        )

    def test_summary_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/v1/expenses/summary/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    
class ExpenseSummaryDateSelectionTests(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="summary_date_user",
            password="StrongPass123!",
        )

        UserSettings.objects.create(
            user=self.user,
            currency="USD",
        )

        self.client.force_authenticate(user=self.user)

    def test_summary_returns_selected_month(self):
        Expense.objects.create(
            user=self.user,
            occurred_on=date(2026, 9, 10),
            amount=Decimal("12.50"),
            currency="USD",
            category="food",
            description="September expense",
        )

        Expense.objects.create(
            user=self.user,
            occurred_on=date(2026, 10, 10),
            amount=Decimal("8.00"),
            currency="USD",
            category="food",
            description="October expense",
        )

        response = self.client.get(
            "/api/v1/expenses/summary/",
            {"year": 2026, "month": 9},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["year"], 2026)
        self.assertEqual(response.data["month"], 9)

        food = next(
            item
            for item in response.data["categories"]
            if item["category"] == "food"
        )

        self.assertEqual(
            Decimal(str(food["spent"])),
            Decimal("12.50"),
        )

    def test_summary_rejects_invalid_month(self):
        response = self.client.get(
            "/api/v1/expenses/summary/",
            {"year": 2026, "month": 13},
        )

        self.assertEqual(response.status_code, 400)

    def test_summary_requires_year_and_month_together(self):
        response = self.client.get(
            "/api/v1/expenses/summary/",
            {"month": 9},
        )

        self.assertEqual(response.status_code, 400)



class ExpenseCSVExportAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="csv_export_user",
            password="StrongPass123!",
        )
        UserSettings.objects.create(
            user=self.user,
            currency="USD",
        )

        self.other_user = User.objects.create_user(
            username="other_csv_user",
            password="StrongPass123!",
        )
        UserSettings.objects.create(
            user=self.other_user,
            currency="USD",
        )

        self.food_expense = Expense.objects.create(
            user=self.user,
            occurred_on=date(2026, 9, 1),
            amount=Decimal("12.50"),
            currency="USD",
            category="food",
            description="Groceries",
        )

        self.transport_expense = Expense.objects.create(
            user=self.user,
            occurred_on=date(2026, 9, 2),
            amount=Decimal("5.00"),
            currency="USD",
            category="transport",
            description="Bus fare",
        )

        self.other_expense = Expense.objects.create(
            user=self.other_user,
            occurred_on=date(2026, 9, 3),
            amount=Decimal("500.00"),
            currency="USD",
            category="food",
            description="Private expense",
        )

        self.client.force_authenticate(user=self.user)

    def read_csv_rows(self, response):
        content = response.content.decode("utf-8-sig")
        return list(csv.DictReader(io.StringIO(content)))

    def test_export_returns_csv_attachment(self):
        response = self.client.get(
            "/api/v1/expenses/export/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response["Content-Type"].startswith("text/csv")
        )
        self.assertIn(
            "attachment;",
            response["Content-Disposition"],
        )

        rows = self.read_csv_rows(response)

        self.assertEqual(len(rows), 2)
        self.assertIn("amount", rows[0])
        self.assertIn("description", rows[0])

    def test_export_contains_only_current_users_expenses(self):
        response = self.client.get(
            "/api/v1/expenses/export/"
        )

        rows = self.read_csv_rows(response)
        exported_ids = {row["id"] for row in rows}

        self.assertEqual(
            exported_ids,
            {
                str(self.food_expense.id),
                str(self.transport_expense.id),
            },
        )
        self.assertNotIn(
            str(self.other_expense.id),
            exported_ids,
        )

    def test_export_respects_category_filter(self):
        response = self.client.get(
            "/api/v1/expenses/export/",
            {"category": "food"},
        )

        self.assertEqual(response.status_code, 200)
        rows = self.read_csv_rows(response)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["category"], "food")
        self.assertEqual(rows[0]["description"], "Groceries")

    def test_export_respects_search_filter(self):
        response = self.client.get(
            "/api/v1/expenses/export/",
            {"search": "Groceries"},
        )

        rows = self.read_csv_rows(response)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["description"], "Groceries")

    def test_export_neutralizes_spreadsheet_formulas(self):
        Expense.objects.create(
            user=self.user,
            occurred_on=date(2026, 9, 4),
            amount=Decimal("1.00"),
            currency="USD",
            category="other",
            description="=1+1",
        )

        response = self.client.get(
            "/api/v1/expenses/export/"
        )
        rows = self.read_csv_rows(response)

        formula_row = next(
            row for row in rows
            if row["description"] == "'=1+1"
        )

        self.assertEqual(
            formula_row["description"],
            "'=1+1",
        )

    def test_export_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/v1/expenses/export/"
        )

        self.assertIn(response.status_code, [401, 403])
