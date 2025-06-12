from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Recipe, Favorite, ShoppingCart, RecipeIngredient
from .serializers import RecipeSerializer, RecipeShortSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
        recipe = self.get_object()
        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response({'errors': 'Рецепт уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
            if not favorite.exists():
                return Response({'errors': 'Рецепт не в избранном'}, status=status.HTTP_400_BAD_REQUEST)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            cart, created = ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
            if not created:
                return Response({'errors': 'Рецепт уже в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            cart = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
            if not cart.exists():
                return Response({'errors': 'Рецепт не в списке покупок'}, status=status.HTTP_400_BAD_REQUEST)
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        link = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        return Response({'short-link': link})  # Изменено на short-link

    # @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    # def download_shopping_cart(self, request):
    #     user = request.user
    #     ingredients = RecipeIngredient.objects.filter(
    #         recipe__shoppingcart_set__user=user
    #     ).values(
    #         'ingredient__name', 'ingredient__measurement_unit'
    #     ).annotate(total_amount=Sum('amount'))
    #     content = 'Список покупок:\n\n'
    #     for ingredient in ingredients:
    #         content += (
    #             f"{ingredient['ingredient__name']} "
    #             f"({ingredient['ingredient__measurement_unit']}) — "
    #             f"{ingredient['total_amount']}\n"
    #         )
    #     response = HttpResponse(content, content_type='text/plain')
    #     response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
    #     return response
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