# your_app_name/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import  Provider,Shipment, Product,ShipmentProduct
from datetime import date
from django.core.exceptions import ValidationError

class ShipmentForm(forms.ModelForm):
    # We will let the user select a consumer for the order
    provider = forms.ModelChoiceField(
        queryset=Provider.objects.all(),
        empty_label="Select a Provider",
        widget=forms.Select(
            attrs={
                "class": "w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:border-none focus:ring-[var(--primary-dark)]"
            }
        ),
    )

    class Meta:
        model = Shipment
        fields = [
            "provider"
        ]  # 'user' will be set automatically in the view, 'status', 'c_date', 'a_date' have defaults/auto_now_add
        widgets = {
            # You can add more specific widgets if needed for other fields
        }


class ShipmentProductForm(forms.ModelForm):
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
        model = ShipmentProduct
        fields = ["product", "quantity"]


# Create an inline formset for OrderProduct related to Order
ShipmentProductFormSet = inlineformset_factory(
    Shipment,  # Parent model
    ShipmentProduct,  # Child model
    form=ShipmentProductForm,
    extra=1,  # Number of empty forms to display initially
    can_delete=True,  # Allow deleting existing order products
    fields=["product", "quantity"],
)

def validate_future_date(value):
    if value < date.today():
        raise ValidationError("Expiration date cannot be in the past!")

class ProductArrivalForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    product_name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': True}),
        required=False
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'quantity-input','readonly': True})
    )
    expire_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'date-input'}),
        validators=[validate_future_date]
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            self.fields['product_name'].initial = kwargs['initial'].get('product_name')
            self.fields['product_id'].initial = kwargs['initial'].get('product_id')

class ProviderForm(forms.ModelForm):
    class Meta: 
        model = Provider 
        fields = ['name']
