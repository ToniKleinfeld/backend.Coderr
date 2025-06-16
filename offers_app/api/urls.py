from django.urls import path
from offers_app.api.views import OfferViewSet

app_name = 'offers'

urlpatterns = [
    path('', OfferViewSet.as_view(), name='offers-list'),
    path('<int:pk>/', OfferViewSet.as_view(), name='offers-detail'),
]