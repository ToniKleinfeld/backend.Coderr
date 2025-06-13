from django.urls import path, include
from reviews_app.api.views import ReviewViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
]
