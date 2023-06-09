from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.paginators import PageLimitPagination
from api.serializers import FollowSerializer, UserCustomSerializer
from core.models import Follow

User = get_user_model()


class UsersViewSet(UserViewSet):
    """Представление для Пользователей"""

    queryset = User.objects.all().order_by('id')
    pagination_class = PageLimitPagination
    serializer_class = UserCustomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(methods=['get'], detail=False, url_path='subscriptions')
    def subscriptions(self, *args, **kwargs):
        queryset = Follow.objects.filter(user=self.request.user)
        pagination = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pagination,
            many=True,
            context={'request': self.request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe')
    def subscribe(self, *args, **kwargs):
        author = get_object_or_404(User, pk=kwargs.get('id'))
        user = self.request.user
        data = {
            'user': user,
            'author': author
        }

        if self.request.method == 'POST':
            if author.id == user.id:
                return Response({'error': 'Вы не можете подписаться на себя.'},
                                status=HTTPStatus.BAD_REQUEST)

            if Follow.objects.filter(**data):
                return Response({'error': 'Вы уже подписаны.'},
                                status=HTTPStatus.BAD_REQUEST)
            obj = Follow.objects.create(**data)
            serializer = FollowSerializer(
                obj,
                many=False,
                context={'request': self.request}
            )
            return Response(serializer.data)

        if self.request.method == 'DELETE':
            obj = Follow.objects.filter(**data)
            if obj.exists():
                obj.delete()
                return Response({'detail': 'Вы отписались.'},
                                status=HTTPStatus.NO_CONTENT)

            else:
                return Response({'error': 'Вы не подписаны.'},
                                status=HTTPStatus.BAD_REQUEST)
