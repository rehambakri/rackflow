from django.contrib import admin
from .models import Consumer , Order ,OrderProduct
# Register your models here.

admin.site.register(Consumer)
admin.site.register(Order)
admin.site.register(OrderProduct)
