"""Application composition root."""

from dataclasses import dataclass

from src.cli import CommandHandler, Menu
from src.config import ApplicationConfig
from src.providers import (
    Clock,
    SystemClock,
    SystemUUIDGenerator,
    UUIDGenerator,
)
from src.services import (
    BudgetService,
    ExpenseTrackerService,
    ExportService,
    SettingsService,
)
from src.storage import JSONStorage


@dataclass(frozen=True)
class Application:
    """Fully composed runtime application and its explicit dependencies."""

    config: ApplicationConfig
    clock: Clock
    uuid_generator: UUIDGenerator
    repository: JSONStorage
    settings_service: SettingsService
    expense_service: ExpenseTrackerService
    budget_service: BudgetService
    export_service: ExportService
    command_handler: CommandHandler
    menu: Menu

    def run(self):
        """Run the configured user interface."""
        self.menu.run()


def create_application(
    config: ApplicationConfig | None = None,
    *,
    clock: Clock | None = None,
    uuid_generator: UUIDGenerator | None = None,
) -> Application:
    """Construct every concrete runtime dependency in one location."""
    config = config or ApplicationConfig.from_environment()
    clock = clock or SystemClock()
    uuid_generator = uuid_generator or SystemUUIDGenerator()

    repository = JSONStorage(
        config.data_dir,
        default_currency=config.default_currency,
        clock=clock,
        uuid_generator=uuid_generator,
    )
    repository.initialize_settings()
    settings_service = SettingsService(repository, repository, repository)
    currency = settings_service.get_currency()
    expense_service = ExpenseTrackerService(
        repository,
        repository,
        clock=clock,
        uuid_generator=uuid_generator,
    )
    budget_service = BudgetService(repository, repository, clock=clock)
    export_service = ExportService(config.export_dir, currency, clock=clock)
    command_handler = CommandHandler(clock)
    menu = Menu(
        settings_service,
        expense_service,
        budget_service,
        export_service,
        command_handler,
        clock,
    )

    return Application(
        config=config,
        clock=clock,
        uuid_generator=uuid_generator,
        repository=repository,
        settings_service=settings_service,
        expense_service=expense_service,
        budget_service=budget_service,
        export_service=export_service,
        command_handler=command_handler,
        menu=menu,
    )
