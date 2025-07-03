from django.db import models
from django.db.models import Sum

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"


class Product(models.Model):
    name = models.CharField("Product Name", max_length=100, null=False, blank=False)

    image = models.ImageField(
        "Product Image",
        upload_to="product_images",
        null=False,
        default="images/product_placeholder.png",
    )

    category = models.ForeignKey(
        to=Category,
        on_delete=models.RESTRICT,
        verbose_name="Product Category",
        null=False,
        blank=False,
    )

    @property
    def quantity(self):
        result = self.productdetails_set.aggregate(total=Sum("quantity"))
        return result["total"] or 0

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "products"


class ProductDetails(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    expire_date = models.DateField(
        auto_now=False, auto_now_add=False, null=False, blank=False
    )
    quantity = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return f"{self.product.name}, {self.quantity}, {self.expire_date}"

    class Meta:
        db_table = "products_details"
        unique_together = ("product", "expire_date")
        verbose_name_plural = "Product details"
