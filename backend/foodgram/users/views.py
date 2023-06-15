from http import HTTPStatus

from api.paginators import PageLimitPagination
from api.serializers import FollowSerializer, UserCustomSerializer
from core.helpers import CustomModelViewSet
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

User = get_user_model()


class UsersViewSet(UserViewSet, CustomModelViewSet):
    """Представление для Пользователей"""

    queryset = User.objects.all().order_by('id')
    pagination_class = PageLimitPagination
    serializer_class = UserCustomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(methods=['get'], detail=False, url_path='subscriptions')
    def subscriptions(self, *args, **kwargs):
        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        pagination = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pagination,
            many=True,
            context={'request': self.request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe')
    def subscribe(self, *args, **kwargs):
        user = self.request.user
        author = User.objects.get(pk=self.kwargs.get('id'))
        obj = user.follower.filter(author=author)
        if self.request.method == 'POST':

            if obj.exists():
                raise ValidationError({'errors': 'Уже подписан.'})
            user.follower.create(author=author)
            serializer = FollowSerializer(
                instance=author,
                context={'request': self.request}
            )
            return Response(serializer.data)

        if self.request.method == 'DELETE':
            obj.delete()
            return Response({'detail': 'Done'}, status=HTTPStatus.NO_CONTENT)
