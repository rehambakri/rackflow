from datetime import datetime

from asgiref.sync import async_to_sync
from authentication.models import CustomUser
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction  # For atomic operations
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from notification.models import Notification
from product.models import Product, ProductDetails
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response

from .forms import (
    ProductArrivalForm,
    ProviderForm,
    ShipmentForm,
    ShipmentProductFormSet,
)
from .models import Provider, Shipment

# Create your views here.


class ShipmentDetails(DetailView):
    model = Shipment
    template_name = "provider/shipmentDetails.html"
    context_object_name = "shipment"


class ListShipmentView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = "provider/list_shipments.html"
    context_object_name = "shipments"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Shipment.objects.all().order_by("-c_date")
        return Shipment.objects.filter(user=user).order_by("-c_date")


class ShipmentCreateView(LoginRequiredMixin, CreateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = "provider/create_shipment.html"
    success_url = reverse_lazy("provider:list_shipments")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["shipment_product_formset"] = ShipmentProductFormSet(
                self.request.POST, self.request.FILES, prefix="shipment_products"
            )
        else:
            context["shipment_product_formset"] = ShipmentProductFormSet(
                prefix="shipment_products"
            )
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data()
        shipment_product_formset = context["shipment_product_formset"]

        # Count valid, non-deleted forms in the formset
        valid_forms = 0
        for sub_form in shipment_product_formset:
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

        if not shipment_product_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            shipment_product_formset.instance = self.object
            shipment_product_formset.save()

        # send websocket a message through channel layer
        # to notify them to start stream new data added to the database

        # get manager user
        manager = CustomUser.objects.filter(is_superuser=True).first()

        # save the notification of product creation in the database
        Notification(
            sender=self.request.user,
            receiver=manager,
            shipment=self.object,
            type="shipment_created",
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


class ShipmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = "provider/update_shipment.html"

    def get_success_url(self):
        return reverse_lazy(
            "provider:list_shipments"
        )  # Adjust to your order list URL name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["shipment_product_formset"] = ShipmentProductFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="shipment_products",
            )
        else:
            context["shipment_product_formset"] = ShipmentProductFormSet(
                instance=self.object, prefix="shipment_products"
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        shipment_product_formset = context["shipment_product_formset"]

        # Check if at least one product exists (not being deleted)
        if self.object.status != "pending":
            form.add_error(
                None, f"Shipment with status {self.object.status} cannot be updated."
            )
            return self.form_invalid(form)
        valid_forms = 0
        for sub_form in shipment_product_formset:
            if (
                sub_form.is_valid()
                and sub_form.cleaned_data
                and not sub_form.cleaned_data.get("DELETE")
            ):
                valid_forms += 1

        if valid_forms < 1:
            form.add_error(None, "Shipment must contain at least one product.")
            return self.form_invalid(form)

        if not shipment_product_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            shipment_product_formset.instance = self.object
            shipment_product_formset.save()

        messages.success(self.request, "Order updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class ShipmentArrivalView(LoginRequiredMixin, UpdateView):
    model = Shipment
    template_name = "provider/process_arrival.html"
    fields = []  # We're not editing the shipment directly

    def get_success_url(self):
        return reverse("provider:list_shipments")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipment = self.object

        # Create a formset for all products in the shipment
        ProductArrivalFormSet = formset_factory(
            ProductArrivalForm, extra=0, can_delete=False
        )

        if self.request.POST:
            context["formset"] = ProductArrivalFormSet(
                self.request.POST, initial=self.get_initial_data()
            )
        else:
            context["formset"] = ProductArrivalFormSet(initial=self.get_initial_data())

        return context

    def get_initial_data(self):
        """Prepare initial data for the formset from shipment products"""
        initial = []
        for product in self.object.shipment_products.all():
            initial.append(
                {
                    "product_id": product.product.id,
                    "product_name": product.product.name,
                    "quantity": product.quantity,
                    "expire_date": None,  # User will fill this
                }
            )
        return initial

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        context = self.get_context_data()
        formset = context["formset"]

        if formset.is_valid():
            with transaction.atomic():
                # Update shipment status
                self.object.status = "arrived"
                self.object.arr_date = timezone.now()
                self.object.save()

                # Process each product in the formset
                for form in formset:
                    product_id = form.cleaned_data["product_id"]
                    quantity = form.cleaned_data["quantity"]
                    expire_date = form.cleaned_data["expire_date"]

                    # Get the product
                    product = Product.objects.get(id=product_id)

                    # Create or update ProductDetails
                    product_detail, created = ProductDetails.objects.get_or_create(
                        product=product,
                        expire_date=expire_date,
                        defaults={"quantity": quantity},
                    )

                    if not created:
                        product_detail.quantity += quantity
                        product_detail.save()

                messages.success(request, "Shipment processed successfully!")
                return redirect(self.get_success_url())

        messages.error(request, "Please correct the errors below.")
        return self.render_to_response(context)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_shipment_status(request, id):
    # Check if user is a manager
    if not request.user.is_staff:
        return Response(
            {"detail": "Only managers can update order status."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Get the order

    shipment = get_object_or_404(Shipment, id=id)
    # Only allow status update if pending
    if shipment.status == "arrived" or shipment.status == "rejected":
        return Response(
            {"detail": "Shipment status cannot be updated."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate new status
    new_status = request.data.get("status", "").lower()
    if new_status not in ["accepted", "rejected", "arrived"]:
        return Response(
            {"detail": "Invalid status provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if new_status in ["accepted", "rejected"] and shipment.status == "pending":
        if new_status == "accepted":
            shipment.a_date = datetime.now()
        shipment.status = new_status
        shipment.save()

    # Send notification
    Notification.objects.create(
        sender=request.user,
        receiver=shipment.user,
        shipment=shipment,
        type="shipment_accepted"
        if new_status == "accepted"
        else ("shipment_arrived" if new_status == "arrived" else "shipment_rejected"),
    )

    # Send WebSocket notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{shipment.user.id}_notification_channels",
        {
            "type": "notification.new",
            "receiver_id": shipment.user.id,
        },
    )

    return Response({"detail": f"Shipment status updated to {new_status}."})

class ProviderCreateView(CreateView):
    model = Provider
    form_class = ProviderForm
    template_name = "provider/create_provider.html"
    success_url = reverse_lazy("provider:list_providers")


class ListProviderView(LoginRequiredMixin, ListView):
    model = Provider
    template_name = "provider/list_providers.html"
    context_object_name = "providers"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Provider.objects.all()
        return Provider.objects.filter(user=user)
