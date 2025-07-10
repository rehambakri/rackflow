# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm , AuthenticationForm
from .models import CustomUser
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name' ) # Add other fields as needed

class CustomUserProfileUpdateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank if you don't want to change the password."
    )
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name' , 'email' ,  'profile_image'  ] # Fields the user can update

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes or other custom styling
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({'class': 'form-control-file'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
                
class CustomAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form that checks the user's 'user_status' field
    after successful authentication.
    """
    def clean(self):
        super().clean() # Call parent's clean to handle default authentication

        user = self.user_cache # Get the authenticated user

        if user is not None:
            if not user.user_status:
                del self.user_cache # Invalidate user_cache to prevent login
                raise forms.ValidationError(
                    "Your account is currently inactive. Please contact support.",
                    code='inactive_account'
                )
        return self.cleaned_data
