from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ProductForm

# Create your views here.
from .models import Product , Category


class ProductList(ListView):
    model = Product
    template_name = "product/index.html"
    context_object_name = "products"
    paginate_by= 10 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context["categories"] = categories
        return context


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
