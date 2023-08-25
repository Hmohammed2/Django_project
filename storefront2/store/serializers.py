from rest_framework import serializers
from decimal import Decimal
from . import models

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField()

class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    
    def calculate_tax(self, product: models.Product):
        return product.unit_price * Decimal(1.10)

class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Cart
        fields = ['id', 'created_at']