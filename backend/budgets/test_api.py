from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserSettings
from budgets.models import Budget


User = get_user_model()


class BudgetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="budget_user",
            password="TestPassword123!",
        )
        UserSettings.objects.create(
            user=self.user,
            currency="USD",
        )

        self.other_user = User.objects.create_user(
            username="other_budget_user",
            password="TestPassword123!",
        )
        UserSettings.objects.create(
            user=self.other_user,
            currency="USD",
        )

        self.client.force_authenticate(user=self.user)

    def test_create_budget(self):
        response = self.client.post(
            "/api/v1/budgets/",
            {
                "category": "food",
                "amount": "200.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        budget = Budget.objects.get(
            user=self.user,
            category="food",
        )

        self.assertEqual(budget.amount, Decimal("200.00"))

    def test_budget_is_assigned_to_authenticated_user(self):
        response = self.client.post(
            "/api/v1/budgets/",
            {
                "user": self.other_user.pk,
                "category": "food",
                "amount": "100.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        budget = Budget.objects.get(pk=response.data["id"])
        self.assertEqual(budget.user, self.user)

    def test_duplicate_category_budget_is_rejected(self):
        Budget.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("100.00"),
        )

        response = self.client.post(
            "/api/v1/budgets/",
            {
                "category": "food",
                "amount": "150.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_non_positive_budget_is_rejected(self):
        response = self.client.post(
            "/api/v1/budgets/",
            {
                "category": "food",
                "amount": "0.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_budget_list_is_scoped_to_authenticated_user(self):
        own_budget = Budget.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("100.00"),
        )

        Budget.objects.create(
            user=self.other_user,
            category="rent",
            amount=Decimal("500.00"),
        )

        response = self.client.get("/api/v1/budgets/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {
            item["id"] for item in response.data["results"]
        }

        self.assertEqual(returned_ids, {own_budget.pk})

    def test_cannot_retrieve_another_users_budget(self):
        other_budget = Budget.objects.create(
            user=self.other_user,
            category="rent",
            amount=Decimal("500.00"),
        )

        response = self.client.get(
            f"/api/v1/budgets/{other_budget.pk}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_budget_amount(self):
        budget = Budget.objects.create(
            user=self.user,
            category="food",
            amount=Decimal("100.00"),
        )

        response = self.client.patch(
            f"/api/v1/budgets/{budget.pk}/",
            {"amount": "150.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        budget.refresh_from_db()
        self.assertEqual(budget.amount, Decimal("150.00"))
