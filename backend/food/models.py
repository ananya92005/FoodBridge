from django.conf import settings
from django.db import models


class FoodStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    MATCHED = "MATCHED", "Matched"
    ASSIGNED = "ASSIGNED", "Assigned"
    COMPLETED = "COMPLETED", "Completed"
    EXPIRED = "EXPIRED", "Expired"
    CANCELLED = "CANCELLED", "Cancelled"


class FoodListing(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="food_listings")
    food_type = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    expiry_time = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=FoodStatus.choices, default=FoodStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.food_type} ({self.quantity})"

