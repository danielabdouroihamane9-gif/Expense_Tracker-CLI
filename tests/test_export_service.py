import csv

import pytest

from src.exceptions import CSVImportError, CurrencyMismatchError, NoDataError
from src.services import ExportService
from tests.fakes import FixedClock, make_expense


def build_service(export_dir, currency="USD"):
    return ExportService(export_dir, currency, clock=FixedClock())


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.reader(handle))


def test_export_expenses_writes_oldest_first_and_filters(tmp_path, sample_expenses):
    service = build_service(tmp_path)
    result = service.export_expenses_to_csv(sample_expenses, "all.csv")
    assert result.record_count == 3 and result.path.name == "all.csv"
    rows = read_csv(tmp_path / "all.csv")
    assert rows[0] == ["Date", "Amount", "Currency", "Category", "Description"]
    assert [row[4] for row in rows[1:]] == ["Concert", "Bus fare", "Lunch"]

    assert service.export_expenses_to_csv(
        sample_expenses, "food.csv", "FOOD"
    ).record_count == 1
    assert read_csv(tmp_path / "food.csv")[1][3] == "food"
    with pytest.raises(NoDataError, match="No expenses"):
        service.export_expenses_to_csv([], "empty.csv")


def test_export_summary_is_sorted_and_includes_total(tmp_path):
    service = build_service(tmp_path)
    assert service.export_summary_to_csv(
        {"transport": 30, "food": 50}, "summary.csv"
    ).kind == "summary"
    assert read_csv(tmp_path / "summary.csv") == [
        ["Category", "Amount", "Currency"],
        ["Food", "50", "USD"],
        ["Transport", "30", "USD"],
        ["Total", "80", "USD"],
    ]
    with pytest.raises(NoDataError, match="No summary"):
        service.export_summary_to_csv({}, "empty.csv")


def test_read_csv_normalizes_headers_and_supports_export_directory(tmp_path):
    service = build_service(tmp_path)
    path = tmp_path / "input.csv"
    path.write_text(" date ,AMOUNT,Category,Description\n2025-01-01,5,food,Lunch\n")
    rows = service.read_expenses_csv(path)
    assert rows == [{"Date": "2025-01-01", "Amount": "5", "Currency": "USD", "Category": "food", "Description": "Lunch"}]


def test_read_csv_preserves_explicit_currency(tmp_path):
    service = build_service(tmp_path)
    path = tmp_path / "currencies.csv"
    path.write_text(
        "Date,Amount,Currency,Category,Description\n"
        "2025-01-01,5,EUR,food,Lunch\n"
    )
    rows = service.read_expenses_csv(path)
    assert rows[0]["Currency"] == "EUR"


def test_export_rejects_expense_in_another_currency(tmp_path):
    service = build_service(tmp_path)
    with pytest.raises(CurrencyMismatchError, match="application currency USD"):
        service.export_expenses_to_csv(
            [make_expense("2025-01-01", 5, "food", "Lunch", currency="EUR")],
            "mixed.csv",
        )
    assert not (tmp_path / "mixed.csv").exists()


def test_read_csv_validation_errors(tmp_path):
    service = build_service(tmp_path)
    with pytest.raises(CSVImportError, match="cannot be empty"):
        service.read_expenses_csv("")
    with pytest.raises(CSVImportError, match="CSV file"):
        service.read_expenses_csv(tmp_path / "input.txt")
    with pytest.raises(CSVImportError, match="does not exist"):
        service.read_expenses_csv(tmp_path / "missing.csv")

    missing = tmp_path / "missing-column.csv"
    missing.write_text("Date,Amount\n2025-01-01,5\n")
    with pytest.raises(CSVImportError, match="Missing columns"):
        service.read_expenses_csv(missing)
    header_only = tmp_path / "header-only.csv"
    header_only.write_text("Date,Amount,Category,Description\n")
    with pytest.raises(CSVImportError, match="empty"):
        service.read_expenses_csv(header_only)
