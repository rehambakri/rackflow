from authentication.forms import CustomUserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from product.models import Product

# Create your views here.


class Add_employee(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("product:list")
    template_name = "add_employee.html"


def is_critical(request):
    critical_products = [p for p in Product.objects.all() if p.is_critical]
    return render(
        request, "list_critical_products.html", {"iscritical": critical_products}
    )
