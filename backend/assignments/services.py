from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from authentication.models import UserRole
from food.models import FoodStatus
from notifications.services import create_notification

from .models import Assignment, AssignmentStatus


def list_assignments_for_user(user):
    queryset = Assignment.objects.select_related("food__donor", "ngo__user").all()
    if user.role == UserRole.DONOR:
        return queryset.filter(food__donor=user)
    if user.role == UserRole.NGO:
        return queryset.filter(ngo__user=user)
    return queryset


def update_assignment_status(user, assignment_id, next_status):
    assignment = get_object_or_404(
        Assignment.objects.select_related("food__donor", "ngo__user"),
        id=assignment_id,
    )
    if user.role == UserRole.NGO:
        if assignment.ngo.user_id != user.id:
            raise PermissionDenied("You can only manage your own assignments.")
    elif user.role != UserRole.ADMIN:
        raise PermissionDenied("Only the assigned NGO or an admin can manage assignments.")

    assignment.status = next_status
    assignment.save(update_fields=["status", "updated_at"])

    if next_status == AssignmentStatus.ACCEPTED:
        assignment.food.status = FoodStatus.ASSIGNED
        assignment.food.save(update_fields=["status", "updated_at"])
        create_notification(
            assignment.food.donor,
            "Assignment accepted",
            f"{assignment.ngo.name} accepted your food listing.",
        )
    elif next_status == AssignmentStatus.REJECTED:
        assignment.food.status = FoodStatus.OPEN
        assignment.food.save(update_fields=["status", "updated_at"])
    elif next_status == AssignmentStatus.COMPLETED:
        assignment.food.status = FoodStatus.COMPLETED
        assignment.food.save(update_fields=["status", "updated_at"])

    return assignment
