from django.db import models


class OfferDetails(models.Model):
    OFFER_TYPE_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    title = models.CharField(max_length=200)
    revisions = models.PositiveIntegerField(default=0, blank=True)
    delivery_time_in_days = models.PositiveIntegerField(default=0, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    # features = models.JSONField(default=[])
    offer_type = models.CharField(
        max_length=20, choices=OFFER_TYPE_CHOICES, default="basic"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Offer Detail"
        verbose_name_plural = "Offer Details"
