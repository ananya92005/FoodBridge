from authentication.models import User


def list_users(role=None):
    queryset = User.objects.all().order_by("id")
    if role:
        queryset = queryset.filter(role=role)
    return queryset

