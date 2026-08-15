"""Tests for validated command-line input collection."""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.cli.commands import CommandHandler


def inputs(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))


def test_date_accepts_valid_value(monkeypatch):
    inputs(monkeypatch, ["2025-06-15"])
    assert CommandHandler.get_user_date() == "2025-06-15"


def test_date_retries_invalid_and_defaults_to_today(monkeypatch, capsys):
    inputs(monkeypatch, ["15/06/2025", ""])
    with patch("src.cli.commands.datetime") as clock:
        clock.strptime.side_effect = datetime.strptime
        clock.now.return_value = datetime(2025, 6, 16)
        assert CommandHandler.get_user_date() == "2025-06-16"
    assert "Invalid format" in capsys.readouterr().out


@pytest.mark.parametrize(
    "method, bad_values, valid, expected, error",
    [
        ("get_user_amount", ["abc", "0", "-2"], "12.5", "12.50", "Invalid amount"),
        ("get_budget_amount", ["abc", "0", "-2"], "250", "250.00", "Invalid amount"),
        ("get_user_category", ["travel"], " FOOD ", "food", "Invalid category"),
        ("get_user_description", ["   "], " Lunch ", "Lunch", "cannot be empty"),
        ("get_user_keyword", ["   "], " taxi ", "taxi", "cannot be empty"),
    ],
)
def test_validated_prompts_retry_until_valid(monkeypatch, capsys, method, bad_values, valid, expected, error):
    inputs(monkeypatch, [*bad_values, valid])
    assert getattr(CommandHandler, method)() == expected
    assert error in capsys.readouterr().out


@pytest.mark.parametrize("entered, expected", [("report.csv", "report.csv"), ("   ", None)])
def test_export_filename_is_optional(monkeypatch, entered, expected):
    inputs(monkeypatch, [entered])
    assert CommandHandler.get_export_filename() == expected


def test_currency_prompt_retries_and_normalizes(monkeypatch, capsys):
    inputs(monkeypatch, ["US", " kmf "])
    assert CommandHandler.get_user_currency() == "KMF"
    assert "Invalid currency" in capsys.readouterr().out


def test_date_range_retries_bad_format_and_reverse_order(monkeypatch, capsys):
    inputs(monkeypatch, ["bad", "2025-01-02", "2025-02-01", "2025-01-01", "2025-01-01", "2025-02-01"])
    start, end = CommandHandler.get_user_date_range()
    assert (str(start), str(end)) == ("2025-01-01", "2025-02-01")
    output = capsys.readouterr().out
    assert "Invalid date format" in output
    assert "cannot be after" in output


@pytest.mark.parametrize("entered, expected", [("0", None), (" data.csv ", "data.csv"), ("", "")])
def test_csv_path_supports_cancel_and_paths(monkeypatch, entered, expected):
    inputs(monkeypatch, [entered])
    assert CommandHandler().get_csv_file_path() == expected
