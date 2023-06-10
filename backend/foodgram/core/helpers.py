import inspect
from http import HTTPStatus

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet

from api.serializers import CropRecipeSerializer


class CustomModelViewSet(ModelViewSet):

    def get_model_object(self, data):
        """Получает объект модели или возвращает ошибку 404"""
        return get_object_or_404(
            self.queryset.model, **data
        )

    def get_filter_set(self, model, data):
        """Получает Модель и словарь для фильтрации."""
        return model.objects.filter(**data)

    def manage_subscription_favorite_cart(self, relate_model):
        """Управление записями о подписках, корзине и избранном,
        на входе функция получает объект класса и
        имя промежуточной модели для записи,
        обрабатывает POST и DELETE запросы,
        возвращая сериализованные данные."""
        data = {'user': self.request.user}
        if str(inspect.currentframe().f_back.f_code.co_name) == 'subscribe':
            data['author'] = self.get_model_object(
                {'pk': self.kwargs.get('id')}
            )
        else:
            data['recipe'] = self.get_model_object(self.request.data)

        if self.request.method == 'POST':
            query = self.get_filter_set(relate_model, data)
            if query.exists():
                raise ValidationError({'errors': 'Объект уже существует.'})
            relate_model.objects.create(**data)
            serializer = CropRecipeSerializer(
                data.get('recipe'),
                many=False,
                context={'request': self.request}
            )
            return Response(serializer.data,
                            status=HTTPStatus.CREATED)

        if self.request.method == 'DELETE':
            query = self.get_filter_set(relate_model, data)
            if not query.exists():
                raise ValidationError({'errors': 'Объект не найден.'})
            query.delete()
            return Response({'detail': 'Удалено'},
                            status=HTTPStatus.NO_CONTENT)
