from django.urls import path
from .views import ProfileDetailView

app_name = "profile"

urlpatterns = [
    path("<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
]
