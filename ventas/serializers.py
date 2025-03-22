from rest_framework import serializers
from .models import Venta, DetalleVenta
from articulos.models import Articulo

class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = ['articulo', 'cantidad', 'precio_unitario']
        extra_kwargs = {
            'precio_unitario': {'required': False}
        }

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'total', 'completada', 'detalles']
        read_only_fields = ['total', 'completada']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        venta = Venta.objects.create(**validated_data)
        total = 0
        for detalle_data in detalles_data:
            articulo = detalle_data['articulo']
            cantidad = detalle_data['cantidad']
            precio_unitario = detalle_data.get('precio_unitario', articulo.precio)
            detalle = DetalleVenta.objects.create(
                venta=venta,
                articulo=articulo,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )
            total += cantidad * precio_unitario
        venta.total = total
        venta.save()
        return venta

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles')
        instance.save()
        DetalleVenta.objects.filter(venta=instance).delete()
        total = 0
        for detalle_data in detalles_data:
            articulo = detalle_data['articulo']
            cantidad = detalle_data['cantidad']
            precio_unitario = detalle_data.get('precio_unitario', articulo.precio)
            detalle = DetalleVenta.objects.create(
                venta=instance,
                articulo=articulo,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )
            total += cantidad * precio_unitario
        instance.total = total
        instance.save()
        return instance