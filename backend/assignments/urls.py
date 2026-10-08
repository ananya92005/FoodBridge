from django.urls import path

from .views import AssignmentActionView, AssignmentListView

urlpatterns = [
    path("", AssignmentListView.as_view(), name="assignment-list"),
    path("<int:assignment_id>/<str:action>/", AssignmentActionView.as_view(), name="assignment-action"),
]

