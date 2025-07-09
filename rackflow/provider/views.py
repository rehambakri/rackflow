from django.shortcuts import render
from .models import Shipment , ShipmentProduct
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class ShipmentDetails(DetailView):
    model = Shipment
    template_name = "shipmentDetails.html"
    context_object_name = "shipment"


class ListShipmentView(LoginRequiredMixin,ListView):
    model = Shipment
    template_name = "provider/list_shipments.html"
    context_object_name = "shipments"

    def get_queryset(self):
        user  = self.request.user
        if user.is_superuser:
            return Shipment.objects.all()
        return Shipment.objects.filter(user=user)


class ShipmentDetails(DetailView):
    model = Shipment
    template_name = "shipmentDetails.html"
    context_object_name = "shipment"




'     