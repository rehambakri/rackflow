from authentication.forms import CustomUserCreationForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from product.models import Product
from authentication.models import CustomUser
from django.views.generic import ListView
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



class ListUsersView(ListView):
    model = CustomUser
    template_name = "list_users.html"
    context_object_name = "users"  

    def get_queryset(self):
        users = super().get_queryset()
        print("Users in DB:", users)
        return users
