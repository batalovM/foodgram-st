from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Recipe, Favorite, ShoppingCart, RecipeIngredient
from .serializers import RecipeSerializer, RecipeShortSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_object(self):
        """
        Переопределяем метод получения объекта для проверки прав доступа при обновлении.
        """
        obj = super().get_object()
        
        # Проверяем права доступа для запросов изменения (PATCH, PUT, DELETE)
        if self.request.method in ['PATCH', 'PUT', 'DELETE'] and obj.author != self.request.user:
            raise PermissionDenied("У вас нет прав для редактирования этого рецепта")
        
        return obj
    
    def update(self, request, *args, **kwargs):
        """
        Переопределяем метод обновления для явной проверки авторства.
        """
        pk = kwargs.get('pk')
    
        # Сначала проверяем существование рецепта без использования get_object()
        recipe_exists = Recipe.objects.filter(pk=pk).exists()
    
        if not recipe_exists:
            # Если рецепт с таким ID не существует, вызываем родительский метод,
            # который вернет 404
            return Response(
                {"detail": "No Recipe matches the given query."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
        # Если рецепт существует, получаем его и проверяем авторство
        instance = Recipe.objects.get(pk=pk)
        if instance.author != request.user:
            return Response(
                {"detail": "У вас нет прав для редактирования этого рецепта"}, 
                status=status.HTTP_403_FORBIDDEN
            )
    
        return super().update(request, *args, **kwargs)
        
    def partial_update(self, request, *args, **kwargs):
        """
        Переопределяем метод частичного обновления для явной проверки авторства.
        """
        pk = kwargs.get('pk')
    
        # Сначала проверяем существование рецепта без использования get_object()
        recipe_exists = Recipe.objects.filter(pk=pk).exists()
    
        if not recipe_exists:
            # Если рецепт с таким ID не существует, вернем 404
            return Response(
                {"detail": "No Recipe matches the given query."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
        # Если рецепт существует, получаем его и проверяем авторство
        instance = Recipe.objects.get(pk=pk)
        if instance.author != request.user:
            return Response(
                {"detail": "У вас нет прав для редактирования этого рецепта"}, 
                status=status.HTTP_403_FORBIDDEN
            )
    
        return super().partial_update(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        author_id = self.request.query_params.get('author')
        if is_favorited == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(favorite__user=self.request.user)  # Исправлено: favorites -> favorite
        if is_in_shopping_cart == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        return queryset

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            try:
                # Получаем рецепт напрямую, без использования self.get_object()
                recipe = get_object_or_404(Recipe, pk=pk)
                
                # Проверяем, не добавлен ли уже рецепт в избранное
                favorite_exists = Favorite.objects.filter(user=request.user, recipe=recipe).exists()
                if favorite_exists:
                    return Response({'errors': 'Рецепт уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Создаем запись в избранном
                Favorite.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeShortSerializer(recipe, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({"detail": "No Recipe matches the given query."}, status=status.HTTP_404_NOT_FOUND)
        
        # Изменяем логику для DELETE - не используем self.get_object()
        if request.method == 'DELETE':
            try:
                # Получаем рецепт напрямую, не используя self.get_object()
                recipe = get_object_or_404(Recipe, pk=pk)
                
                # Проверяем наличие рецепта в избранном
                favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
                if not favorite.exists():
                    return Response({'errors': 'Рецепт не в избранном'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Удаляем запись
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({"detail": "No Recipe matches the given query."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            try:
                # Получаем рецепт напрямую, без использования self.get_object()
                recipe = get_object_or_404(Recipe, pk=pk)
                
                # Проверяем, не добавлен ли уже рецепт в корзину
                cart_exists = ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists()
                if cart_exists:
                    return Response({'errors': 'Рецепт уже в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Создаем запись в корзине
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeShortSerializer(recipe, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({"detail": "No Recipe matches the given query."}, status=status.HTTP_404_NOT_FOUND)
        
        # Изменяем логику для DELETE - не используем self.get_object()
        if request.method == 'DELETE':
            try:
                # Получаем рецепт напрямую, не используя self.get_object()
                recipe = get_object_or_404(Recipe, pk=pk)
                
                # Проверяем наличие рецепта в корзине
                cart = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
                if not cart.exists():
                    return Response({'errors': 'Рецепт не в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Удаляем запись
                cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({"detail": "No Recipe matches the given query."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        link = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        return Response({'short-link': link})  # Изменено на short-link

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user  # Исправлено: shoppingcart_set -> shopping_cart
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        content = 'Список покупок:\n\n'
        for ingredient in ingredients:
            content += (
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) — "
                f"{ingredient['total_amount']}\n"
            )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response