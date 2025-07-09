from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order
# Create your views here.

class OrderDetails(DetailView):
    model = Order
    template_name = "orderDetails.html"
    context_object_name = "order"


class ListOrderView(LoginRequiredMixin,ListView):
    model = Order
    template_name = "consumer/list_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        user  = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=user)

