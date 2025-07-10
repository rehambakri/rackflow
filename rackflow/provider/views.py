from django.shortcuts import render
from .models import Shipment 
from .models import Provider
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ShipmentForm,ShipmentProductFormSet
from django.db import transaction # For atomic operations

# Create your views here.

class ShipmentDetails(DetailView):
    model = Shipment
    template_name = "shipmentDetails.html"
    context_object_name = "shipment"


class ListShipmentView(LoginRequiredMixin,ListView):
    model = Shipment
    template_name = "provider/list_shipments.html"
    context_object_name = "shipments"

    def get_queryset(self):
        user  = self.request.user
        if user.is_superuser:
            return Shipment.objects.all()
        return Shipment.objects.filter(user=user)


class ShipmentDetails(DetailView):
    model = Shipment
    template_name = "provider/shipmentDetails.html"
    context_object_name = "shipment"


class ShipmentCreateView(LoginRequiredMixin, CreateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = 'provider/create_shipment.html'
    success_url = reverse_lazy('provider:list_shipments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['shipment_product_formset'] = ShipmentProductFormSet(self.request.POST, self.request.FILES, prefix='shipment_products')
        else:
            context['shipment_product_formset'] = ShipmentProductFormSet(prefix='shipment_products')
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data()
        shipment_product_formset = context['shipment_product_formset']
        
        # Count valid, non-deleted forms in the formset
        valid_forms = 0
        for sub_form in shipment_product_formset:
            if sub_form.is_valid() and sub_form.cleaned_data and not sub_form.cleaned_data.get('DELETE'):
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

        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class ListProviderView(LoginRequiredMixin, ListView):
    model = Provider
    template_name = "provider/list_providers.html"
    context_object_name = "providers"

    def get_queryset(self):
        user  = self.request.user
        if user.is_superuser:
            return Provider.objects.all()
        return Provider.objects.filter(user=user)