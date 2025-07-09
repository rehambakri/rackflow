from authentication.models import CustomUser
from django.db import models


class Notification(models.Model):
    # I named it to_who, in case we want to implement broadcasting the same
    # notifications to multiple users, which in this case will have another
    # property called from_who. But right now only the manage will get
    # notifications so no need to that yet
    # Don't delete past notification from user just because it was deleted (RESTRICT)

    CHOICES = [
        ("product_created", "Product Created Notification"),
        ("product_deleted", "Product Deleted Notification"),
        ("product_updated", "Product Updated Notification"),
        ("order_created", "Order Created Notification"),
        ("shipment_created", "Shipment Created Notification"),
    ]

    to_who = models.ForeignKey(
        CustomUser,
        null=False,
        blank=False,
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
    # we need to save the content into the database to reterieve it later if
    # the socket reconnects...
    content = models.TextField(null=False, blank=False)

    class Meta:
        db_table = "notifications"
