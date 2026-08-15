import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import MagicMock

import pytest

import src.main as application
from src.application import create_application
from src.config import ApplicationConfig
from src.exceptions import DomainValidationError
from src.storage import DataCorruptionError
from tests.fakes import FixedClock, SequentialUUIDGenerator


def test_module_runs_and_exits_when_windows_output_is_redirected(tmp_path):
    repository_root = Path(__file__).parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(repository_root)

    completed = subprocess.run(
        [sys.executable, "-m", "src.main"],
        input=b"0\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=tmp_path,
        env=environment,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr.decode(errors="replace")
    assert b"Goodbye" in completed.stdout


def test_composition_wires_one_repository_and_runtime_providers(tmp_path):
    config = ApplicationConfig(tmp_path / "data", tmp_path / "exports", "usd")
    clock = FixedClock()
    uuid_generator = SequentialUUIDGenerator()
    composed = create_application(
        config,
        clock=clock,
        uuid_generator=uuid_generator,
    )
    repository = composed.repository

    assert composed.expense_service.expense_repository is repository
    assert composed.budget_service.budget_repository is repository
    assert composed.settings_service.settings_repository is repository
    assert composed.expense_service.clock is clock
    assert composed.budget_service.clock is clock
    assert composed.export_service.clock is clock
    assert composed.command_handler.clock is clock
    assert composed.menu.clock is clock
    assert composed.config.default_currency == "USD"
    assert composed.menu.currency == "USD"


def test_main_runs_menu(monkeypatch):
    composed = MagicMock()
    monkeypatch.setattr(
        application, "create_application", MagicMock(return_value=composed)
    )
    application.main()
    composed.run.assert_called_once_with()


@pytest.mark.parametrize("error, code, message", [(KeyboardInterrupt(), 0, "interrupted"), (RuntimeError("boom"), 1, "boom")])
def test_main_converts_failures_to_exit_codes(monkeypatch, capsys, error, code, message):
    composed = MagicMock()
    composed.run.side_effect = error
    monkeypatch.setattr(
        application, "create_application", MagicMock(return_value=composed)
    )
    with pytest.raises(SystemExit) as caught:
        application.main()
    assert caught.value.code == code
    assert message in capsys.readouterr().out


def test_main_reports_startup_persistence_failure(monkeypatch, capsys):
    monkeypatch.setattr(
        application,
        "create_application",
        MagicMock(side_effect=DataCorruptionError("damaged expenses")),
    )

    with pytest.raises(SystemExit) as caught:
        application.main()

    assert caught.value.code == 1
    output = capsys.readouterr().out
    assert "could not access its data safely" in output
    assert ".bak backups" in output


def test_main_reports_expected_application_startup_failure(monkeypatch, capsys):
    monkeypatch.setattr(
        application,
        "create_application",
        MagicMock(side_effect=DomainValidationError("invalid configuration")),
    )

    with pytest.raises(SystemExit) as caught:
        application.main()

    assert caught.value.code == 1
    assert "could not start" in capsys.readouterr().out
