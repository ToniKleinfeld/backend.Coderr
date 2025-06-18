from django.urls import path, include
from rest_framework.routers import DefaultRouter
from offers_app.api.views import OfferDetailsView

app_name = "offerdetails"

router = DefaultRouter()
router.register(r"", OfferDetailsView, basename="offerdetails")

urlpatterns = [
    path("", include(router.urls)),
]
