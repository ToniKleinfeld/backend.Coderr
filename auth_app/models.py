from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):

    class UserType(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CUSTOMER,
    )

    def __str__(self):
        return self.username
