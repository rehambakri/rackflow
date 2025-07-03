from django.shortcuts import render
from django.views.generic import ListView

# Create your views here.
from .models import Product


class ProductList(ListView):
    model = Product
    template_name = "product/index.html"
    context_object_name = "products"
