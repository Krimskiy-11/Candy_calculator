from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import IngredientViewSet, CakeViewSet

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('cakes', CakeViewSet, basename='cake')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
