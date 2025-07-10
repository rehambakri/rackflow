from authentication.forms import CustomUserCreationForm , CustomUserProfileUpdateForm
from django.shortcuts import render , get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView ,UpdateView
from product.models import Product
from authentication.models import CustomUser

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

class UpdateEmployeeProfileView(UpdateView):
    model = CustomUser
    form_class = CustomUserProfileUpdateForm 
    template_name = "update_user_profile.html"
    context_object_name = "profile"
    success_url = reverse_lazy("dashboard") 

