from datetime import datetime

from asgiref.sync import async_to_sync
from authentication.models import CustomUser
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction  # For atomic operations
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from notification.models import Notification
from product.models import ProductDetails
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response

from .forms import ConsumerForm, OrderForm, OrderProductFormSet
from .models import Consumer, Order

# Create your views here.


class OrderDetails(DetailView):
    model = Order
    template_name = "consumer/orderDetails.html"
    context_object_name = "order"


class ListOrderView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "consumer/list_orders.html"
    context_object_name = "orders"
    ordering = ["id"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all().order_by("-c_date")
        return Order.objects.filter(user=user).order_by("-c_date")


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "consumer/create_order.html"
    success_url = reverse_lazy("consumer:list_orders")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["order_product_formset"] = OrderProductFormSet(
                self.request.POST, self.request.FILES, prefix="order_products"
            )
        else:
            context["order_product_formset"] = OrderProductFormSet(
                prefix="order_products"
            )
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data()
        order_product_formset = context["order_product_formset"]

        # Count valid, non-deleted forms in the formset
        valid_forms = 0
        for sub_form in order_product_formset:
            if (
                sub_form.is_valid()
                and sub_form.cleaned_data
                and not sub_form.cleaned_data.get("DELETE")
            ):
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

        # send websocket a message through channel layer
        # to notify them to start stream new data added to the database

        # get manager user
        manager = CustomUser.objects.filter(is_superuser=True).first()

        # save the notification of product creation in the database
        Notification(
            sender=self.request.user,
            receiver=manager,
            order=self.object,
            type="order_created",
        ).save()

        # notify all manager sockets to stream the latest added new notification record
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "manager_notification_channels",
            {
                "type": "notification.new",
                "receiver_id": manager.id,
            },
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "consumer/update_order.html"

    def get_success_url(self):
        return reverse_lazy(
            "consumer:list_orders"
        )  # Adjust to your order list URL name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["order_product_formset"] = OrderProductFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="order_products",
            )
        else:
            context["order_product_formset"] = OrderProductFormSet(
                instance=self.object, prefix="order_products"
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        order_product_formset = context["order_product_formset"]

        # Check if at least one product exists (not being deleted)
        if self.object.status != "pending":
            form.add_error(
                None, f"Order with status {self.object.status} cannot be updated."
            )
            return self.form_invalid(form)
        valid_forms = 0
        for sub_form in order_product_formset:
            if (
                sub_form.is_valid()
                and sub_form.cleaned_data
                and not sub_form.cleaned_data.get("DELETE")
            ):
                valid_forms += 1

        if valid_forms < 1:
            form.add_error(None, "Order must contain at least one product.")
            return self.form_invalid(form)

        if not order_product_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            order_product_formset.instance = self.object
            order_product_formset.save()

        messages.success(self.request, "Order updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_order_status(request, id):
    # Check if user is a manager
    if not request.user.is_staff:
        return Response(
            {"detail": "Only managers can update order status."},
             status=status.HTTP_403_FORBIDDEN,
        )

    # Get the order
    order = get_object_or_404(Order, id=id)

    # Only allow status update if pending
    if order.status != "pending":
        return Response(
            {"detail": "Order status cannot be updated."},
             status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate new status
    new_status = request.data.get("status", "").lower()
    if new_status not in ["accepted", "rejected"]:
        return Response(
            {"detail": "Invalid status provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # If order is accepted, reduce product quantities (FIFO)
    if new_status == "accepted":
        try:
            # Get all order items
            order_items = order.order_products.all()

            for item in order_items:
                product = item.product
                remaining_quantity = item.quantity

                # Get ProductDetails sorted by nearest expiry date (FIFO)
                product_details = ProductDetails.objects.filter(
                    product=product
                ).order_by("expire_date")

                # If not enough stock, reject the order
                if remaining_quantity > product.quantity:
                    order.status = "rejected"
                    order.save()
                    return Response(
                        {
                            "detail": f"Insufficient stock for {product.name}. Order rejected."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                # Deduct quantities starting from nearest expiry
                for detail in product_details:
                    if remaining_quantity <= 0:
                        break  # No more quantity to deduct

                    if detail.quantity >= remaining_quantity:
                        # Deduct full remaining quantity
                        detail.quantity -= remaining_quantity
                        detail.save()
                        remaining_quantity = 0
                    else:
                        # Deduct all available and move to next expiry
                        remaining_quantity -= detail.quantity
                        detail.quantity = 0
                        detail.save()

        except Exception as e:
            print(f"Error updating inventory: {str(e)}")
            return Response(
                {"detail": f"Error updating inventory: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Update order status
    order.status = new_status
    order.a_date = datetime.now()
    order.save()

    # Send notification
    Notification.objects.create(
        sender=request.user,
        receiver=order.user,
        order=order,
        type="order_accepted" if new_status == "accepted" else "order_rejected",
    )

    # Send WebSocket notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{order.user.id}_notification_channels",
        {
            "type": "notification.new",
            "receiver_id": order.user.id,
        },
    )

    return Response({"detail": f"Order status updated to {new_status}."})


class ConsumerCreateView(CreateView):
    model = Consumer
    form_class = ConsumerForm
    template_name = "consumer/create_consumer.html"
    success_url = reverse_lazy("consumer:list_consumers")


class ListConsumerView(LoginRequiredMixin, ListView):
    model = Consumer
    template_name = "consumer/list_consumers.html"
    context_object_name = "consumers"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Consumer.objects.all()
        return Consumer.objects.filter(user=user)
