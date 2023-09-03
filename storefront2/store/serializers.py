from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from . import models


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    
    def calculate_tax(self, product: models.Product):
        return product.unit_price * Decimal(1.10)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context["product_id"]
        models.Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField("calculate_price")
    
    class Meta:
        model = models.CartItem
        fields = ["id", "product", "quantity", "total_price"]

    def calculate_price(self, cart_item: models.CartItem):
        return cart_item.quantity * cart_item.product.unit_price


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ["quantity"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product with that given id")
        return value

    def save(self, **kwargs):
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]
        cart_id = self.context["cart_id"]

        #  same logic as genericviewset save method. Assign instance to new cart item
        try: 
            # update existing cart_id
            cart_item = models.CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        
        except models.CartItem.DoesNotExist:
            # If no cartitem is found, this logic will create one
            self.instance = models.CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = models.CartItem
        fields = ["id", "product_id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)

    total_price = serializers.SerializerMethodField("get_total_price")

    class Meta:
        model = models.Cart
        fields = ['id', "items", "total_price"]

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()]) 
    
class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = models.OrderItem
        fields = ['id','product', 'unit_price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = models.Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not models.Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given id was found')
        if models.CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("cart is empty")
        return cart_id

    ''' Creates an order, validates it against the cart id. Returns information storing it into variable order items which uses list comprehension.\
    delete cart afterwards 
    '''
    def save(self, **kwargs):
        # wrapping up function in transaction.atomic. Makes it so either all the code gets executed or if something goes wrong all changes get rolled back.
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            # Tuple unpacking
            (customer,  created) = models.Customer.objects.get_or_create(user_id=self.context['user_id'])
            order = models.Order.objects.create(customer=customer)
        
            cart_items = models.CartItem.objects.filter(
                cart_id=cart_id
            )

            order_items = [
                models.OrderItem(
                        order=order,
                        product = item.product,
                        unit_price= item.quantity,
                        quantity=item.quantity
            ) for item in cart_items]

            models.OrderItem.objects.bulk_create(order_items)
            models.Cart.objects.filter(pk=cart_id).delete()

            return order