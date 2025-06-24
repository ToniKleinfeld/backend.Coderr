"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from orders_app.api.views import OrderCountView, CompletedOrderCountView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("auth_app.api.urls")),
    path("api/profile/", include("profiles_app.api.urls")),
    path("api/profiles/", include("profiles_app.api.profiles_urls")),
    path("api/offers/", include("offers_app.api.urls")),
    path("api/offerdetails/", include("offers_app.api.offerdetails_urls")),
    path("api/orders/", include("orders_app.api.urls")),
    path("api/order-count/<int:business_user_id>/", OrderCountView.as_view(), name="order-count"),
    path(
        "api/completed-order-count/<int:business_user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-order-count",
    ),
    path("api/reviews/", include("reviews_app.api.urls")),
]
