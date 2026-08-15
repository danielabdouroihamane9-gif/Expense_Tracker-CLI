"""Persistence-free test doubles for service boundary tests."""


class InMemoryRepository:
    """Implement all three repository contracts without file or JSON behavior."""

    def __init__(self, currency="USD"):
        self.expenses = []
        self.budgets = {}
        self.settings = {"currency": currency}

    def load_expenses(self):
        return self.expenses.copy()

    def save_expenses(self, expenses):
        self.expenses = list(expenses)

    def load_budgets(self):
        return self.budgets.copy()

    def save_budgets(self, budgets):
        self.budgets = dict(budgets)

    def load_settings(self):
        return self.settings.copy()

    def save_settings(self, settings):
        self.settings = dict(settings)
