from django.db import models


class AssignmentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    COMPLETED = "COMPLETED", "Completed"


class Assignment(models.Model):
    food = models.ForeignKey("food.FoodListing", on_delete=models.CASCADE, related_name="assignments")
    ngo = models.ForeignKey("ngo.NGO", on_delete=models.CASCADE, related_name="assignments")
    status = models.CharField(max_length=20, choices=AssignmentStatus.choices, default=AssignmentStatus.PENDING)
    match_score = models.FloatField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("food", "ngo")

    def __str__(self):
        return f"Assignment #{self.id}"

