from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ProductForm

# Create your views here.
from .models import Product


class ProductList(ListView):
    model = Product
    template_name = "product/index.html"
    context_object_name = "products"


class ProductCreate(CreateView):
    form_class = ProductForm
    model = Product
    template_name = "product/create.html"
    context_object_name = "products"
    success_url = reverse_lazy("product:list")


class ProductUpdate(UpdateView):
    form_class = ProductForm
    model = Product
    template_name = "product/update.html"
    context_object_name = "products"
    success_url = reverse_lazy("product:list")
