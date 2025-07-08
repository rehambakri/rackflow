from django.shortcuts import render
from django.views.generic import ListView
from .models import Order
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.


class ListOrderView(LoginRequiredMixin,ListView):
    model = Order
    template_name = "consumer/list_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        user  = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=user)

