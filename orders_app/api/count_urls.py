from django.urls import path, include
from orders_app.api.views import OrderCountView

app_name = "count_urls"

urlpatterns = [
    path("order-count/<int:business_user_id>/", OrderCountView.as_view(), name="order-count"),
]
