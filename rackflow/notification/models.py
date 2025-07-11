from authentication.models import CustomUser
from consumer.models import Order
from django.db import models
from product.models import Product
from provider.models import Shipment


class Notification(models.Model):
    CHOICES = [
        # these are sent to the manager (if he is not the sender. Don't send the
        # manager notifications about actions he has done)
        ("product_created", "Product Created Notification"),
        ("order_created", "Order Created Notification"),
        ("shipment_created", "Shipment Created Notification"),
        # these are sent to the users who made them
        ("order_accepted", "Order Accepted Notification"),
        ("shipment_accepted", "Shipment Accepted Notification"),
        ("order_rejected", "Order Rejected Notification"),
        ("shipment_rejected", "Shipment Rejected Notification"),
    ]

    sender = models.ForeignKey(
        CustomUser,
        null=False,
        blank=False,
        on_delete=models.RESTRICT,
        related_name="sender",
    )

    # Don't delete past notification from user just because it was deleted (RESTRICT)
    receiver = models.ForeignKey(
        CustomUser,
        null=False,
        blank=False,
        on_delete=models.RESTRICT,
        related_name="reciever",
    )

    # Don't delete past notifications of a product just because it was deleted (RESTRICT)
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.RESTRICT,
        related_name="notifications",
    )

    order = models.ForeignKey(
        Order,
        null=True,
        on_delete=models.RESTRICT,
        related_name="notifications",
    )

    shipment = models.ForeignKey(
        Shipment,
        null=True,
        on_delete=models.RESTRICT,
        related_name="notifications",
    )

    type = models.CharField(
        "Notification Type",
        max_length=100,
        null=False,
        blank=False,
        choices=CHOICES,
    )

    created_date_time = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        db_table = "notifications"
