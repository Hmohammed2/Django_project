from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from . import views

router = DefaultRouter()

router.register('products', views.ProductViewSet, basename="products")
router.register('collections', views.CollectionViewSet)

products_router = NestedDefaultRouter(parent_router=router, parent_prefix="products", lookup='product')
products_router.register("reviews", views.ReviewViewSet, basename='product-reviews')

# URLConf
urlpatterns = router.urls + products_router.urls
