from django.shortcuts import render
from .models import ohipment , OhipmentProduct
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView
# Create your views here.

class orderDetails(DetailView):
    model = order
    template_name = "orderDetails.html"
    context_object_name = "order"