from django.shortcuts import render
from .models import Shipment , ShipmentProduct
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView

# Create your views here.

class ShipmentDetails(DetailView):
    model = Shipment
    template_name = "shipmentDetails.html"
    context_object_name = "shipment"




'     