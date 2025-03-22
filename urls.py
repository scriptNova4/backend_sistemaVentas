"""
URL configuration for puntoDeVenta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from articulos.views import ArticuloViewSet, CategoriaViewSet, ProveedorViewSet
from ventas.views import VentaViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view
from rest_framework.response import Response

router = DefaultRouter()
router.register(r'articulos', ArticuloViewSet, basename='articulos')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'proveedores', ProveedorViewSet, basename='proveedores')
router.register(r'ventas', VentaViewSet, basename='ventas')

@api_view(['GET'])
def api_root(request):
    return Response({
        'articulos': request.build_absolute_uri('v1/articulos/'),
        'categorias': request.build_absolute_uri('v1/categorias/'),
        'proveedores': request.build_absolute_uri('v1/proveedores/'),
        'ventas': request.build_absolute_uri('v1/ventas/'),
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api_root'),  # Vista raíz sin autenticación
    path('api/v1/', include(router.urls)),    # Prefijo para las rutas del router
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]