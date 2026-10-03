from rest_framework import serializers
from .models import Ingredient, Cake, CakeIngredient


class IngredientSerializer(serializers.ModelSerializer):
    cost_per_unit = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)

    class Meta:
        model = Ingredient
        fields = '__all__'


class CakeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient', write_only=True
    )

    class Meta:
        model = CakeIngredient
        fields = ['id', 'ingredient', 'ingredient_id', 'component', 'quantity']


# class CakeDecorationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CakeDecoration
#         fields = '__all__'


class CakeSerializer(serializers.ModelSerializer):
    cake_ingredients = CakeIngredientSerializer(many=True, required=False)

    class Meta:
        model = Cake
        fields = ['id', 'name', 'base_diameter', 'description', 'cake_ingredients', 'created_at']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('cake_ingredients', [])
        cake = Cake.objects.create(**validated_data)
        for item in ingredients_data:
            CakeIngredient.objects.create(
                cake=cake,
                ingredient=item['ingredient'],
                component=item.get('component', 'biscuit'),
                quantity=item['quantity']
            )
        return cake


class CostCalculationSerializer(serializers.Serializer):
    target_diameter = serializers.IntegerField()
    scale_factor = serializers.FloatField()
    net_weight_kg = serializers.DecimalField(max_digits=8, decimal_places=2)
    ingredients_by_layer = serializers.DictField()
    packaging = serializers.ListField()
    ingredients_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    packaging_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    cost_per_kg = serializers.DecimalField(max_digits=12, decimal_places=2)
    price_per_kg = serializers.DecimalField(max_digits=12, decimal_places=2)
    cake_sale_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    final_client_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2)

