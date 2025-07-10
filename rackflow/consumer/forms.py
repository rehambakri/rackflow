# your_app_name/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderProduct, Product, Consumer


class OrderForm(forms.ModelForm):
    # We will let the user select a consumer for the order
    consumer = forms.ModelChoiceField(
        queryset=Consumer.objects.all(),
        empty_label="Select a Consumer",
        widget=forms.Select(
            attrs={
                "class": "w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:border-none focus:ring-[var(--primary-dark)]"
            }
        ),
    )

    class Meta:
        model = Order
        fields = [
            "consumer"
        ]  # 'user' will be set automatically in the view, 'status', 'c_date', 'a_date' have defaults/auto_now_add
        widgets = {
            # You can add more specific widgets if needed for other fields
        }


class OrderProductForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        empty_label="Select a Product",
        widget=forms.Select(
            attrs={
                "class": "w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:border-none focus:ring-[var(--primary-dark)] max-h-[400px]",
            }
        ),
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:border-none focus:ring-[var(--primary-dark)]",
                "placeholder": "Quantity",
            }
        ),
    )

    class Meta:
        model = OrderProduct
        fields = ["product", "quantity"]


# Create an inline formset for OrderProduct related to Order
OrderProductFormSet = inlineformset_factory(
    Order,  # Parent model
    OrderProduct,  # Child model
    form=OrderProductForm,
    extra=1,  # Number of empty forms to display initially
    can_delete=True,  # Allow deleting existing order products
    fields=["product", "quantity"],
)
