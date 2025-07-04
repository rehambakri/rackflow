from django.contrib import admin
from .models import Provider, Shipment, ShipmentProduct
# Register your models here.

admin.site.register(Provider)
admin.site.register(Shipment)
admin.site.register(ShipmentProduct)
