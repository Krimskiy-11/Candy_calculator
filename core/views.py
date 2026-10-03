from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ingredient, Cake
from .serializers import IngredientSerializer, CakeSerializer, CostCalculationSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class CakeViewSet(viewsets.ModelViewSet):
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer

    @action(detail=True, methods=['get'])
    def calculate(self, request, pk=None):
        """GET /api/cakes/{id}/calculate/?diameter=24"""
        cake = self.get_object()
        diameter = request.query_params.get('diameter') or cake.base_diameter
        result = cake.calculate_cost(int(diameter))
        return Response(CostCalculationSerializer(result).data)

