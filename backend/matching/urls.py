from django.urls import path

from .views import MatchPreviewView

urlpatterns = [path("preview/", MatchPreviewView.as_view(), name="match-preview")]
