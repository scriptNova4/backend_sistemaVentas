from django.db import models
from articulos.models import Articulo


class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    completada = models.BooleanField(default=False)

    def __str__(self):
        return f"Venta {self.id} - {self.fecha}"

    class Meta:
        ordering = ['-fecha']

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Detalle de venta {self.venta.id} - Artículo {self.articulo.id}"

    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            self.precio_unitario = self.articulo.precio
        super().save(*args, **kwargs)