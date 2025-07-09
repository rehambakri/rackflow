from authentication.models import CustomUser
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from product.models import Product, ProductDetails

# Create your models here.


class Consumer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)

    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "consumers"
        verbose_name_plural = "conumers"


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)

    STATUS_CHOICE = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("canceled", "Canceled"),
    ]

    consumer = models.ForeignKey(
        Consumer, on_delete=models.RESTRICT, related_name="orders"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="pending")
    c_date = models.DateTimeField(auto_now_add=True)
    a_date = models.DateField(null=True, blank=True)

    product = models.ManyToManyField(
        Product, through="OrderProduct", related_name="orders"
    )

    @property
    def quantity(self):
        result = self.order_products.aggregate(total=Sum("quantity"))
        return result["total"] or 0

    """ def change_status(self, new_status):
        self.status = new_status
        if self.status == "accepted" and self.a_date is None:
            self.a_date = timezone.now()
        self.save()
        return self.status


    def check_expire_date(self, request, id):
        order = get_object_or_404(Order, pk=id)
        if order.status == "accepted":
            for product in order.product.all():
                expire_date = self.product_details.expire_date
                if expire_date and order.a_date:
                    difference = (expire_date - order.a_date).days
                    if difference <= 4:
                        order.status = "canceled"
                        order.save()
                        return order.status
            return order.status
    """

    def __str__(self):
        return (
            f"Order #{self.id} - Consumer: {self.consumer.name} - Status: {self.status}"
        )

    class Meta:
        db_table = "orders"
        verbose_name_plural = "orders"


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_products"
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "order_products"
        verbose_name_plural = "order_products"
        unique_together = ("order", "product")

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in order #{self.order.id}"
