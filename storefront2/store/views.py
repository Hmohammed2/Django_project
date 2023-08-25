from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {"request": self.request}
    
    # Override the delete function within the generic view as it contains some logic not present.
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() > 0:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    # Override the delete function within the generic view as it contains some logic not present.
    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({"error": "Cannot delete collection as it contains more than 1 product"})
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def create_cart(request):

    return Response("ok")