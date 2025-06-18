from django.urls import path, include
from rest_framework.routers import DefaultRouter
from offers_app.api.views import OfferViewSet

app_name = "offers"

router = DefaultRouter()
router.register(r"", OfferViewSet, basename="offers")

urlpatterns = [
    path("", include(router.urls)),
]
