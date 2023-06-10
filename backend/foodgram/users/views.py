from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.paginators import PageLimitPagination
from api.serializers import FollowSerializer, UserCustomSerializer
from core.helpers import CustomModelViewSet
from core.models import Follow

User = get_user_model()


class UsersViewSet(UserViewSet, CustomModelViewSet):
    """Представление для Пользователей"""

    queryset = User.objects.all().order_by('id')
    pagination_class = PageLimitPagination
    serializer_class = UserCustomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(methods=['get'], detail=False, url_path='subscriptions')
    def subscriptions(self, *args, **kwargs):
        pagination = self.paginate_queryset(
            self.get_filter_set(Follow,
                                {'user': self.request.user})
        )
        serializer = FollowSerializer(
            pagination,
            many=True,
            context={'request': self.request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe')
    def subscribe(self, *args, **kwargs):
        return self.manage_subscription_favorite_cart(Follow)
