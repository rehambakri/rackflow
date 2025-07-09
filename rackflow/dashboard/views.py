from django.shortcuts import render
from product.models import Product
from product.views import ProductList
# Create your views here.



def add_employee(request):
        return render(request, 'add_employee.html')

def is_critical(request):
    critical_products = [p for p in Product.objects.all() if p.is_critical]
    return render(request, 'list_critical_products.html', {
        'iscritical': critical_products
    })