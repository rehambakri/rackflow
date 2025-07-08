from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from .forms import ProductForm

# Create your views here.
from .models import Product , Category


class ProductList(ListView):
    model = Product
    template_name = "product/index.html"
    context_object_name = "products"
    paginate_by= 10 

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get all filter parameters from request
        params = {
            "search": self.request.GET.get("search"),
            "category": self.request.GET.get("category"),
            "items": self.request.GET.get("items"),
        }
        # Apply search filter (name only as per your model)
        if params["search"]:
            queryset = queryset.filter(name__icontains=params["search"])

        # Apply category filter
        if params["category"]:
            queryset = queryset.filter(category__name=params["category"])
        # Update pagination size
        if params["items"] and params["items"].isdigit():
            self.paginate_by = int(params["items"])

        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add all categories to context
        context["categories"] = Category.objects.all().distinct()

        # Preserve current filter values
        context["current_filters"] = {
            "search_query": self.request.GET.get("search", ""),
            "category_query": self.request.GET.get("category", ""),
            "items_query": self.paginate_by,
        }

        return context
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     categories = Category.objects.all()
    #     context["categories"] = categories
    #     return context


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


class ProductDetails(DetailView):
    model = Product
    template_name = "product/details.html"
    context_object_name = "product"
    success_url = reverse_lazy("product:details")

