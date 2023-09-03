from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from . import views

router = DefaultRouter()

router.register('products', views.ProductViewSet, basename="products")
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

products_router = NestedDefaultRouter(parent_router=router, parent_prefix="products", lookup='product')
products_router.register("reviews", views.ReviewViewSet, basename='product-reviews')
carts_router = NestedDefaultRouter(parent_router=router, parent_prefix="carts", lookup='cart')
carts_router.register("items", views.CartItemViewSet, basename='cart-items')

# URLConf
urlpatterns = router.urls + products_router.urls + carts_router.urls
