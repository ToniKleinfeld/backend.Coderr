from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


# Create your models here.
class Review(models.Model):
    """
    Model for customer reviews of business users, including rating and description.
    """

    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="business_review"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviewer_review"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    description = models.CharField(max_length=150, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

        unique_together = ('business_user', 'reviewer')

    def __str__(self):
        return f"Review from {self.reviewer.username} to {self.business_user.username} - {self.rating}/5"
