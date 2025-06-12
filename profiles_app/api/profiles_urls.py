from django.urls import path
from .views import BusinessProfileListView, CustomerProfileListView

app_name = 'profiles'

urlpatterns = [
    path('business/', BusinessProfileListView.as_view(), name='business-profiles-list'),
    path('customer/', CustomerProfileListView.as_view(), name='customer-profiles-list'),
]