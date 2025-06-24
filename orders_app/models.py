from django.db import models
from django.contrib.auth import get_user_model
from offers_app.models import Offer

User = get_user_model()


class Order(models.Model):
    """
    Model representing an order placed by a user for an offer.
    """

    status_choices = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_user_orders")
    customer_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="customer_user_orders")
    offer_detail = models.ForeignKey("offers_app.OfferDetail", on_delete=models.CASCADE, related_name="order")
    status = models.CharField(max_length=20, choices=status_choices, default="in_progress")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer_user.username}"
