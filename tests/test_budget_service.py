import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from src.services import BudgetService
from src.exceptions import DomainValidationError
from src.storage import JSONStorage, StorageWriteError


def build_service(data_dir):
    repository = JSONStorage(data_dir)
    return BudgetService(repository, repository)


def test_budget_crud_and_persistence(tmp_path):
    service = build_service(tmp_path)
    result = service.set_budget(" FOOD ", "250.129")
    assert result.category == "food"
    assert result.amount == Decimal("250.13")
    assert service.get_budget("food") == Decimal("250.13")
    assert service.get_all_budgets() == {"food": Decimal("250.13")}
    assert build_service(tmp_path).get_budget("FOOD") == Decimal("250.13")
    assert service.delete_budget("missing") is False
    assert service.delete_budget("FOOD") is True
    assert service.clear_all_budgets() is True


@pytest.mark.parametrize("category, amount", [("invalid", 10), ("food", 0), ("food", "bad")])
def test_invalid_budget_is_reported(category, amount, tmp_path):
    service = build_service(tmp_path)
    with pytest.raises(DomainValidationError):
        service.set_budget(category, amount)
    assert service.get_all_budgets() == {}


def test_budget_status_boundaries(tmp_path):
    service = build_service(tmp_path)
    for category in ("food", "rent", "transport", "shopping"):
        service.set_budget(category, 100)
    status = service.get_budget_status({"food": 79, "rent": 80, "transport": 100, "shopping": 101})

    assert status["food"]["warning"] is False
    assert status["rent"]["warning"] is True
    assert status["transport"]["limit"] is True
    assert status["transport"]["over_budget"] is False
    assert status["shopping"]["over_budget"] is True
    assert status["shopping"]["remaining"] == -1


def test_failed_saves_roll_back_every_budget_mutation(tmp_path):
    service = build_service(tmp_path)
    service.budgets = {
        "food": Decimal("100.00"),
        "rent": Decimal("500.00"),
    }
    before = service.budgets.copy()
    service.budget_repository.save_budgets = MagicMock(
        side_effect=StorageWriteError("simulated disk failure")
    )

    with pytest.raises(StorageWriteError):
        service.set_budget("food", 200)
    assert service.budgets == before

    with pytest.raises(StorageWriteError):
        service.set_budget("transport", 50)
    assert service.budgets == before

    with pytest.raises(StorageWriteError):
        service.delete_budget("food")
    assert service.budgets == before

    with pytest.raises(StorageWriteError):
        service.clear_all_budgets()
    assert service.budgets == before
