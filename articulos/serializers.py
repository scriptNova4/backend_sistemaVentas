from rest_framework import serializers
from .models import Articulo, Categoria, Proveedor, Venta, VentaItem

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

class ArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = ['id', 'codigobarra', 'nombre', 'descripcion', 'precio', 'stock', 'fecha_creacion', 'categoria', 'proveedor']
        read_only_fields = ['fecha_creacion']

    def validate_codigobarra(self, value):
        instance = self.instance
        if instance and instance.codigobarra == value:
            return value
        if Articulo.objects.filter(codigobarra=value).exists():
            raise serializers.ValidationError("El código de barras ya existe. Por favor, usa uno diferente.")
        return value

    def validate(self, data):
        if float(data.get('precio', 0)) <= 0:
            raise serializers.ValidationError({"precio": "El precio debe ser mayor que 0."})
        if int(data.get('stock', 0)) < 0:
            raise serializers.ValidationError({"stock": "El stock no puede ser negativo."})
        return data

class VentaItemSerializer(serializers.ModelSerializer):
    articulo = ArticuloSerializer(read_only=True)
    articulo_id = serializers.PrimaryKeyRelatedField(
        queryset=Articulo.objects.all(), source='articulo', write_only=True
    )

    class Meta:
        model = VentaItem
        fields = ['id', 'articulo', 'articulo_id', 'cantidad', 'precio_unitario']

    def validate(self, data):
        articulo = data['articulo']
        cantidad = data['cantidad']
        if cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        if cantidad > articulo.stock:
            raise serializers.ValidationError(f"No hay suficiente stock para {articulo.nombre}. Stock disponible: {articulo.stock}")
        return data

class VentaSerializer(serializers.ModelSerializer):
    items = VentaItemSerializer(many=True)

    class Meta:
        model = Venta
        fields = ['id', 'cliente', 'fecha', 'total', 'items']
        read_only_fields = ['fecha', 'total']  # total será calculado en create

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        venta = Venta.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            articulo = item_data['articulo']
            cantidad = item_data['cantidad']
            precio_unitario = articulo.precio
            total += precio_unitario * cantidad
            VentaItem.objects.create(
                venta=venta,
                articulo=articulo,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )
            articulo.stock -= cantidad
            articulo.save()
        venta.total = total
        venta.save()
        return venta

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items')
        instance.cliente = validated_data.get('cliente', instance.cliente)
        
        for item in instance.items.all():
            item.articulo.stock += item.cantidad
            item.articulo.save()
        
        instance.items.all().delete()
        
        total = 0
        for item_data in items_data:
            articulo = item_data['articulo']
            cantidad = item_data['cantidad']
            precio_unitario = articulo.precio
            total += precio_unitario * cantidad
            VentaItem.objects.create(
                venta=instance,
                articulo=articulo,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )
            articulo.stock -= cantidad
            articulo.save()
        
        instance.total = total
        instance.save()
        return instance