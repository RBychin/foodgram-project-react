from http import HTTPStatus

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet

from api.serializers import CropRecipeSerializer


class CustomModelViewSet(ModelViewSet):

    def get_filter_set(self, model, data):
        """Получает Модель и словарь для фильтрации."""
        return model.objects.filter(**data)

    def manage_favorite_cart(self, relate_model):
        """Управление записями о подписках, корзине и избранном,
        на входе функция получает объект класса и
        имя промежуточной модели для записи,
        обрабатывает POST и DELETE запросы,
        возвращая сериализованные данные."""
        user = self.request.user
        obj = self.get_object()
        data = {'user': user, 'recipe': obj}
        query = relate_model.objects.filter(user=user, recipe=obj)
        if self.request.method == 'POST':
            if query.exists():
                raise ValidationError({'errors': 'Объект уже существует.'})
            relate_model.objects.create(**data)
            serializer = CropRecipeSerializer(
                instance=obj,
                context={'request': self.request}
            )
            return Response(serializer.data, status=HTTPStatus.CREATED)

        if self.request.method == 'DELETE':
            if not query.exists():
                raise ValidationError({'errors': 'Объект не найден.'})
            query.delete()
            return Response({'detail': 'Done'},
                            status=HTTPStatus.NO_CONTENT)
