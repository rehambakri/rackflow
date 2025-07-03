from django.contrib import admin

# Register your models here.
from .models import Category, Product, ProductDetails

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductDetails)
