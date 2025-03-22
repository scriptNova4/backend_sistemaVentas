from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from .models import Venta, DetalleVenta
from .serializers import VentaSerializer, DetalleVentaSerializer
from articulos.models import Articulo
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Comentado para desarrollo

    @transaction.atomic
    def perform_create(self, serializer):
        try:
            logger.debug(f"Datos recibidos: {self.request.data}")
            detalles_data = self.request.data.get('detalles', [])
            venta = serializer.save()
            total = 0
            for detalle in detalles_data:
                articulo = Articulo.objects.get(id=detalle['articulo'])
                if articulo.stock < detalle['cantidad']:
                    raise ValidationError(
                        f"Stock insuficiente para el artículo {articulo.id}. "
                        f"Disponible: {articulo.stock}, Solicitado: {detalle['cantidad']}"
                    )
                subtotal = articulo.precio * detalle['cantidad']
                DetalleVenta.objects.create(
                    venta=venta,
                    articulo=articulo,
                    cantidad=detalle['cantidad'],
                    precio_unitario=articulo.precio
                )
                articulo.stock -= detalle['cantidad']
                articulo.save()
                total += subtotal
            venta.total = total
            venta.save()
        except Articulo.DoesNotExist as e:
            raise ValidationError(f"No existe el artículo especificado: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error al procesar la venta: {str(e)}")

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        venta = self.get_object()
        if venta.completada:
            return Response(
                {"error": "No se puede eliminar una venta completada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Restaurar el stock de los artículos
        for detalle in venta.detalleventa_set.all():
            articulo = detalle.articulo
            articulo.stock += detalle.cantidad
            articulo.save()
        return super().destroy(request, *args, **kwargs)