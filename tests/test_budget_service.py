import pytest

from src.services import BudgetService


def test_budget_crud_and_persistence(tmp_path):
    service = BudgetService(tmp_path)
    assert "Budget set" in service.set_budget(" FOOD ", "250.129")
    assert service.get_budget("food") == 250.13
    assert service.get_all_budgets() == {"food": 250.13}
    assert BudgetService(tmp_path).get_budget("FOOD") == 250.13
    assert service.delete_budget("missing") is False
    assert service.delete_budget("FOOD") is True
    assert service.clear_all_budgets() is True


@pytest.mark.parametrize("category, amount", [("invalid", 10), ("food", 0), ("food", "bad")])
def test_invalid_budget_is_reported(category, amount, tmp_path):
    service = BudgetService(tmp_path)
    assert "Invalid" in service.set_budget(category, amount)
    assert service.get_all_budgets() == {}


def test_budget_status_boundaries(tmp_path):
    service = BudgetService(tmp_path)
    for category in ("food", "rent", "transport", "shopping"):
        service.set_budget(category, 100)
    status = service.get_budget_status({"food": 79, "rent": 80, "transport": 100, "shopping": 101})

    assert status["food"]["warning"] is False
    assert status["rent"]["warning"] is True
    assert status["transport"]["limit"] is True
    assert status["transport"]["over_budget"] is False
    assert status["shopping"]["over_budget"] is True
    assert status["shopping"]["remaining"] == -1
