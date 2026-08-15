from unittest.mock import MagicMock

import pytest

import src.main as application
from src.storage import DataCorruptionError


def test_main_runs_menu(monkeypatch):
    menu = MagicMock()
    monkeypatch.setattr(application, "Menu", MagicMock(return_value=menu))
    application.main()
    menu.run.assert_called_once_with()


@pytest.mark.parametrize("error, code, message", [(KeyboardInterrupt(), 0, "interrupted"), (RuntimeError("boom"), 1, "boom")])
def test_main_converts_failures_to_exit_codes(monkeypatch, capsys, error, code, message):
    menu = MagicMock()
    menu.run.side_effect = error
    monkeypatch.setattr(application, "Menu", MagicMock(return_value=menu))
    with pytest.raises(SystemExit) as caught:
        application.main()
    assert caught.value.code == code
    assert message in capsys.readouterr().out


def test_main_reports_startup_persistence_failure(monkeypatch, capsys):
    monkeypatch.setattr(
        application,
        "Menu",
        MagicMock(side_effect=DataCorruptionError("damaged expenses")),
    )

    with pytest.raises(SystemExit) as caught:
        application.main()

    assert caught.value.code == 1
    output = capsys.readouterr().out
    assert "could not access its data safely" in output
    assert ".bak backups" in output
