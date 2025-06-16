from django.urls import path
from offers_app.api.views import OfferDetailsView

app_name = 'offerdetails'

urlpatterns = [
    path('<int:pk>/', OfferDetailsView.as_view(), name='offerdetails-detail'),
]