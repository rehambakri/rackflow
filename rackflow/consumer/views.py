from django.views.generic import DetailView, ListView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from notification.models import Notification
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response

from .models import Order

from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction # For atomic operations

from .forms import OrderForm, OrderProductFormSet
class OrderDetails(DetailView):
    model = Order
    template_name = "consumer/orderDetails.html"
    context_object_name = "order"


class ListOrderView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "consumer/list_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=user)

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'consumer/create_order.html'
    success_url = reverse_lazy('consumer:list_orders')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['order_product_formset'] = OrderProductFormSet(self.request.POST, self.request.FILES, prefix='order_products')
        else:
            context['order_product_formset'] = OrderProductFormSet(prefix='order_products')
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data()
        order_product_formset = context['order_product_formset']
        
        # Count valid, non-deleted forms in the formset
        valid_forms = 0
        for sub_form in order_product_formset:
            if sub_form.is_valid() and sub_form.cleaned_data and not sub_form.cleaned_data.get('DELETE'):
                valid_forms += 1
        
        # Check if there's at least one valid product
        if valid_forms < 1:
            form.add_error(None, "You must add at least one product to the order.")
            return self.form_invalid(form)
        
        if not order_product_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            order_product_formset.instance = self.object
            order_product_formset.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_order_status(request, id):
    # check if user is a manager
    manager = request.user
    if not manager.is_staff:  # change to custom check if needed
        return Response(
            {"detail": "Only managers can update order status."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # get the order
    order = get_object_or_404(Order, id=id)

    # only allow status update if it's currently pending
    if order.status != "pending":
        return Response(
            {"detail": "Order status cannot be updated."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # update status (e.g., to accepted)
    new_status = request.data.get("status", "").lower()
    if new_status not in [
        "accepted",
        "rejected",
    ]:  # or whatever your allowed values are
        return Response(
            {"detail": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    order.status = new_status
    order.a_date = datetime.now()
    order.save()

    # send notification to the user who created the order
    Notification.objects.create(
        sender=manager,
        receiver=order.user,
        order=order,
        type="order_accepted" if new_status == "accepted" else "order_rejected",
    )

    # send websocket notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{order.user.id}_notification_channels",
        {
            "type": "notification.new",
            "receiver_id": order.user.id,
        },
    )
    return Response({"detail": f"Order status updated to {new_status}."})
