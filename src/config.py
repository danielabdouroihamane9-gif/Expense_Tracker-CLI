"""Centralized runtime configuration for the expense tracker."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from src.utils import validate_currency


DATA_DIR_ENV = "EXPENSE_TRACKER_DATA_DIR"
EXPORT_DIR_ENV = "EXPENSE_TRACKER_EXPORT_DIR"
DEFAULT_CURRENCY_ENV = "EXPENSE_TRACKER_DEFAULT_CURRENCY"


@dataclass(frozen=True)
class ApplicationConfig:
    """Validated filesystem and initial-currency configuration."""

    data_dir: Path
    export_dir: Path
    default_currency: str = "USD"

    def __post_init__(self):
        object.__setattr__(self, "data_dir", Path(self.data_dir))
        object.__setattr__(self, "export_dir", Path(self.export_dir))
        object.__setattr__(
            self, "default_currency", validate_currency(self.default_currency)
        )

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
        base_dir: str | Path | None = None,
    ) -> "ApplicationConfig":
        """Build configuration from environment variables and safe defaults.

        Relative paths are resolved from ``base_dir``. The current working
        directory is used only here, at the configuration boundary, to retain
        the CLI's existing default behavior.
        """
        values = os.environ if environ is None else environ
        root = Path.cwd() if base_dir is None else Path(base_dir)
        root = root.expanduser().resolve()

        def resolve_path(name: str, default: str) -> Path:
            raw_value = values.get(name, "").strip()
            configured = Path(raw_value or default).expanduser()
            if not configured.is_absolute():
                configured = root / configured
            return configured.resolve()

        return cls(
            data_dir=resolve_path(DATA_DIR_ENV, "data"),
            export_dir=resolve_path(EXPORT_DIR_ENV, "exports"),
            default_currency=values.get(DEFAULT_CURRENCY_ENV, "USD"),
        )
