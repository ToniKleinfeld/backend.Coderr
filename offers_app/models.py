from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="offers/images/", null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def min_price(self):
        return self.details.aggregate(models.Min("price"))["price__min"]

    @property
    def min_delivery_time(self):
        return self.details.aggregate(models.Min("delivery_time_in_days"))[
            "delivery_time_in_days__min"
        ]


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=100)
    revisions = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    delivery_time_in_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    features = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["price"]
        unique_together = [
            "offer",
            "offer_type",
        ]

    def __str__(self):
        return f"{self.offer.title} - {self.get_offer_type_display()}"
