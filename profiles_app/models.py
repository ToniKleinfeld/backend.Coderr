from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    """
    Profil model extension for more user information
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        primary_key=True,  # Profile ID = User ID
    )
    file = models.CharField(blank=False, default="profile_picture.jpg")
    location = models.CharField(max_length=50, blank=True, default="")
    tel = models.CharField(max_length=15, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def id(self):
        return self.user.pk

    @property
    def username(self):
        return self.user.username

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email or ""

    @property
    def type(self):
        return self.user.type

    @property
    def created_at(self):
        return self.user.date_joined
