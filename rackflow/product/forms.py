from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--background)] focus:border-gray-300"
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--background)] focus:border-gray-300"
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "w-full p-3 rounded-xl border border-gray-300 flex flex-row justify-between focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--background)] focus:border-gray-300"
                }
            ),
        }
