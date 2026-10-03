from decimal import Decimal
from django.db import models


class Unit(models.TextChoices):
    GRAM = 'g', 'г'
    MILLILITER = 'ml', 'мл'
    PIECE = 'pcs', 'шт'


class ComponentType(models.TextChoices):
    BISCUIT = 'biscuit', 'Бисквит'
    CREAM = 'cream', 'Крем / Прослойка'
    FILLING = 'filling', 'Начинка / Конфи'
    SOAK = 'soak', 'Пропитка'
    COATING = 'coating', 'Выравнивание (ганаш/крем-чиз)'
    DECOR = 'decor', 'Декор'


class Ingredient(models.Model):
    name = models.CharField('Название продукта', max_length=150)
    package_price = models.DecimalField('Цена закупки', max_digits=10, decimal_places=2)
    package_quantity = models.DecimalField('Фасовка упаковки', max_digits=10, decimal_places=2)
    unit = models.CharField('Ед. изм.', max_length=5, choices=Unit.choices, default=Unit.GRAM)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f"{self.name} ({self.package_price} ₽ / {self.package_quantity} {self.unit})"

    @property
    def cost_per_unit(self) -> Decimal:
        if self.package_quantity and self.package_quantity > 0:
            return self.package_price / self.package_quantity
        return Decimal('0.00')


class Cake(models.Model):
    name = models.CharField('Название торта', max_length=200)
    base_diameter = models.PositiveIntegerField('Базовый диаметр (см)', default=18)
    bake_loss_factor = models.DecimalField('Коэфф. выхода с учетом упёка', max_digits=4, decimal_places=2, default=Decimal('0.90'))
    labor_markup = models.DecimalField('Наценка за работу (1.0 = +100%)', max_digits=4, decimal_places=2, default=Decimal('1.00'))
    description = models.TextField('Этапы приготовления', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_cost(self, target_diameter: int | None = None) -> dict:
        if not target_diameter:
            target_diameter = self.base_diameter

        # Коэффициент площади круга: (D_new / D_base) ** 2
        k = Decimal((target_diameter / self.base_diameter) ** 2)

        ingredients_by_layer = {}
        total_ingredients_cost = Decimal('0.00')
        raw_ingredients_weight_g = Decimal('0.00')
        decor_weight_g = Decimal('0.00')

        for item in self.cake_ingredients.select_related('ingredient').all():
            scaled_qty = (item.quantity * k).quantize(Decimal('0.1'))
            cost = (scaled_qty * item.ingredient.cost_per_unit).quantize(Decimal('0.01'))
            total_ingredients_cost += cost

            # Для граммов и мл считаем вес
            if item.ingredient.unit in [Unit.GRAM, Unit.MILLILITER]:
                raw_ingredients_weight_g += scaled_qty
                if item.component == ComponentType.DECOR:
                    decor_weight_g += scaled_qty

            layer_name = item.get_component_display()
            ingredients_by_layer.setdefault(layer_name, []).append({
                'name': item.ingredient.name,
                'quantity': scaled_qty,
                'unit': item.ingredient.get_unit_display(),
                'cost': cost,
            })

        # Формула веса из вашей таблицы: (Вес_сырья * 0.9) - Декор (в кг)
        net_weight_kg = (
            ((raw_ingredients_weight_g * self.bake_loss_factor) - decor_weight_g) / Decimal('1000')
        ).quantize(Decimal('0.01'))
        if net_weight_kg <= 0:
            net_weight_kg = Decimal('1.00')

        # Расходники и упаковка (коробка, подложка, лента)
        packaging_data = []
        total_packaging_cost = Decimal('0.00')
        for pack in self.packaging_items.all():
            cost = (pack.price * pack.quantity).quantize(Decimal('0.01'))
            total_packaging_cost += cost
            packaging_data.append({
                'name': pack.name,
                'quantity': pack.quantity,
                'price': pack.price,
                'cost': cost
            })

        # Экономика:
        # Себестоимость 1 кг торта
        cost_per_kg = (total_ingredients_cost / net_weight_kg).quantize(Decimal('0.01'))
        # Цена 1 кг с работой
        price_per_kg = (cost_per_kg * (Decimal('1.00') + self.labor_markup)).quantize(Decimal('0.01'))
        # Стоимость торта без упаковки
        cake_sale_price = (price_per_kg * net_weight_kg).quantize(Decimal('0.01'))
        # ИТОГО к оплате клиенту
        final_client_price = cake_sale_price + total_packaging_cost
        # Чистая прибыль кондитера
        net_profit = final_client_price - total_ingredients_cost - total_packaging_cost

        return {
            'target_diameter': target_diameter,
            'scale_factor': round(float(k), 2),
            'net_weight_kg': net_weight_kg,
            'ingredients_by_layer': ingredients_by_layer,
            'packaging': packaging_data,
            'ingredients_total': total_ingredients_cost,
            'packaging_total': total_packaging_cost,
            'cost_per_kg': cost_per_kg,
            'price_per_kg': price_per_kg,
            'cake_sale_price': cake_sale_price,
            'final_client_price': final_client_price,
            'net_profit': net_profit,
        }


class CakeIngredient(models.Model):
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE, related_name='cake_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    component = models.CharField(
        'Слой / назначение',
        max_length=20,
        choices=ComponentType.choices,
        default=ComponentType.BISCUIT
    )
    quantity = models.DecimalField('Количество на базовый диаметр', max_digits=10, decimal_places=2)


class PackagingItem(models.Model):
    """Расходники торта: коробка, подложка, лента, кондитерские мешки."""
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE, related_name='packaging_items')
    name = models.CharField('Наименование (Коробка, Подложка и т.д.)', max_length=150)
    quantity = models.DecimalField('Количество', max_digits=6, decimal_places=1, default=1.0)
    price = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2)
