from django.views.generic import DetailView, ListView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
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


class ListOrderView(LoginRequiredMixin,ListView):
    model = Order
    template_name = "consumer/list_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        user  = self.request.user
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