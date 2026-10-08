from rest_framework import response, status, views
from rest_framework.exceptions import ValidationError

from .models import AssignmentStatus
from .serializers import AssignmentSerializer
from .services import list_assignments_for_user, update_assignment_status


class AssignmentListView(views.APIView):
    def get(self, request):
        assignments = list_assignments_for_user(request.user)
        return response.Response(AssignmentSerializer(assignments, many=True).data)


class AssignmentActionView(views.APIView):
    def post(self, request, assignment_id, action):
        action_map = {
            "accept": AssignmentStatus.ACCEPTED,
            "reject": AssignmentStatus.REJECTED,
            "complete": AssignmentStatus.COMPLETED,
        }
        next_status = action_map.get(action)
        if next_status is None:
            raise ValidationError({"action": "Choose accept, reject, or complete."})
        assignment = update_assignment_status(request.user, assignment_id, next_status)
        return response.Response(AssignmentSerializer(assignment).data, status=status.HTTP_200_OK)
