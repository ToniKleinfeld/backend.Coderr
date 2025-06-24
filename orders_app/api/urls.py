from django.urls import path, include
from orders_app.api.views import OrderViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", OrderViewSet, basename="orders")

app_name = "orders"

urlpatterns = [
    path("", include(router.urls)),
]
