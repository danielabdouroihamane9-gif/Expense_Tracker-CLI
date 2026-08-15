import csv

from src.services import ExportService


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.reader(handle))


def test_export_expenses_writes_oldest_first_and_filters(tmp_path, sample_expenses):
    service = ExportService(tmp_path)
    assert "Exported 3 expenses" in service.export_expenses_to_csv(sample_expenses, "all.csv")
    rows = read_csv(tmp_path / "all.csv")
    assert rows[0] == ["Date", "Amount", "Currency", "Category", "Description"]
    assert [row[4] for row in rows[1:]] == ["Concert", "Bus fare", "Lunch"]

    assert "Exported 1 expenses" in service.export_expenses_to_csv(sample_expenses, "food.csv", "FOOD")
    assert read_csv(tmp_path / "food.csv")[1][3] == "food"
    assert "No expenses" in service.export_expenses_to_csv([], "empty.csv")


def test_export_summary_is_sorted_and_includes_total(tmp_path):
    service = ExportService(tmp_path)
    assert "Exported summary" in service.export_summary_to_csv({"transport": 30, "food": 50}, "summary.csv")
    assert read_csv(tmp_path / "summary.csv") == [
        ["Category", "Amount", "Currency"],
        ["Food", "50", "USD"],
        ["Transport", "30", "USD"],
        ["Total", "80", "USD"],
    ]
    assert "No summary" in service.export_summary_to_csv({}, "empty.csv")


def test_read_csv_normalizes_headers_and_supports_export_directory(tmp_path):
    service = ExportService(tmp_path)
    path = tmp_path / "input.csv"
    path.write_text(" date ,AMOUNT,Category,Description\n2025-01-01,5,food,Lunch\n")
    success, rows, errors = service.read_expenses_csv(path)
    assert success is True and errors == []
    assert rows == [{"Date": "2025-01-01", "Amount": "5", "Currency": "USD", "Category": "food", "Description": "Lunch"}]


def test_read_csv_preserves_explicit_currency(tmp_path):
    service = ExportService(tmp_path)
    path = tmp_path / "currencies.csv"
    path.write_text(
        "Date,Amount,Currency,Category,Description\n"
        "2025-01-01,5,EUR,food,Lunch\n"
    )
    success, rows, errors = service.read_expenses_csv(path)
    assert success is True and errors == []
    assert rows[0]["Currency"] == "EUR"


def test_export_rejects_expense_in_another_currency(tmp_path):
    from src.models import Expense

    service = ExportService(tmp_path, currency="USD")
    result = service.export_expenses_to_csv(
        [Expense("2025-01-01", 5, "food", "Lunch", currency="EUR")],
        "mixed.csv",
    )
    assert "application currency USD" in result
    assert not (tmp_path / "mixed.csv").exists()


def test_read_csv_validation_errors(tmp_path):
    service = ExportService(tmp_path)
    assert service.read_expenses_csv("") == (False, [], [])
    assert "CSV" in service.read_expenses_csv(tmp_path / "input.txt")[2][0]
    assert "does not exist" in service.read_expenses_csv(tmp_path / "missing.csv")[2][0]

    missing = tmp_path / "missing-column.csv"
    missing.write_text("Date,Amount\n2025-01-01,5\n")
    assert "Missing columns" in service.read_expenses_csv(missing)[2][0]
    header_only = tmp_path / "header-only.csv"
    header_only.write_text("Date,Amount,Category,Description\n")
    assert "empty" in service.read_expenses_csv(header_only)[2][0]
