from authentication.models import CustomUser
from django.db import models
from django.db.models import Sum
from product.models import Product


class Provider(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "providers"
        verbose_name_plural = "providers"


class Shipment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("arrived", "Arrived"),
        ("canceled", "Canceled"),
    ]

    provider = models.ForeignKey(
        to=Provider, on_delete=models.RESTRICT, related_name="shipments"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    c_date = models.DateTimeField(auto_now_add=True)
    a_date = models.DateTimeField(
        null=True,
        blank=True,
    )
    arr_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    products = models.ManyToManyField(
        Product,
        through="ShipmentProduct",
        related_name="shipments",
    )

    @property
    def quantity(self):
        result = self.shipment_products.aggregate(total=Sum("quantity"))
        return result["total"] or 0

    class Meta:
        db_table = "shipments"
        verbose_name_plural = "shipments"

    def __str__(self):
        return f"Shipment #{self.id} - Provider: {self.provider.name} - Status: {self.status}"


class ShipmentProduct(models.Model):
    shipment = models.ForeignKey(
        Shipment, on_delete=models.CASCADE, related_name="shipment_products"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "shipment_products"
        verbose_name_plural = "shipment_products"
        unique_together = ("shipment", "product")

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in Shipment #{self.shipment.id}"
