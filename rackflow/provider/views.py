from django.shortcuts import render
from django.views.generic import ListView
from .models import Shipment
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.


class ListShipmentView(LoginRequiredMixin,ListView):
    model = Shipment
    template_name = "provider/list_shipments.html"
    context_object_name = "shipments"

    def get_queryset(self):
        user  = self.request.user
        if user.is_superuser:
            return Shipment.objects.all()
        return Shipment.objects.filter(user=user)

