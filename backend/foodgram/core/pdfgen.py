from core.models import RecipeIngredient
from django.db.models import Sum


def pdf_dw(request):
    """Функция создает список покупок и генерирует txt файл."""

    user = request.user

    ingredient_counts = RecipeIngredient.objects.filter(
        recipe__recipe_in_cart__user=user
    ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
        total_amount=Sum('amount')
    )
    total_cooking_time = user.cart.all().aggregate(
        total_cooking_time=Sum('recipe__cooking_time')
    )

    total_time = total_cooking_time['total_cooking_time']
    hours = total_time // 60
    minutes = total_time % 60

    content = ((f'Список покупок для пользователя '
                f'{user.first_name} {user.last_name}\n'
               f'Покупки для рецептов:') + '\n - '
               "\n - ".join(
                   [recipe.recipe.name for recipe in user.cart.all()]
               )
               + '\n\n')
    for ingredient in ingredient_counts:
        name = ingredient['ingredient__name']
        amount = ingredient['total_amount']
        unit = ingredient['ingredient__measurement_unit']
        content += f'\n☐ {name} - {amount} - {unit}'

    content += (f'\n\nОбщее время приготовления составит: '
                f'{hours}ч. {minutes}мин.')

    return content
