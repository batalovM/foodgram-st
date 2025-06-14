from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ["^name"]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name_filter = self.request.query_params.get("name")
        if name_filter:
            queryset = queryset.filter(name__istartswith=name_filter)
        return queryset
