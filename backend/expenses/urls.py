from rest_framework.routers import DefaultRouter

from .views import ExpenseViewSet
from budgets.views import BudgetViewSet

router = DefaultRouter()
router.register("expenses", ExpenseViewSet, basename="expense")

router.register(
    "budgets",
    BudgetViewSet,
    basename="budget",
)

urlpatterns = router.urls
