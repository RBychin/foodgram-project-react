from django.contrib.auth import get_user_model
from djoser.views import UserViewSet

from users.serializers import CustomUserSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
