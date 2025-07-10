from authentication.forms import CustomUserCreationForm , CustomUserProfileUpdateForm
from django.shortcuts import render , get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView ,UpdateView
from product.models import Product
from authentication.models import CustomUser
from django.http import JsonResponse

# Create your views here.


class Add_employee(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("product:list")
    template_name = "add_employee.html"


def is_critical(request):
    critical_products = [p for p in Product.objects.all() if p.is_critical]
    return render(
        request, "list_critical_products.html", {"iscritical": critical_products}
    )

class UpdateEmployeeProfileView(UpdateView):
    model = CustomUser
    form_class = CustomUserProfileUpdateForm 
    template_name = "update_user_profile.html"
    context_object_name = "profile"
    success_url = reverse_lazy("dashboard") 

def toggle_user_status(request, pk):
    """
    AJAX view to toggle the user_status of a UserProfile.
    Accessible only by staff/superusers.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)

    try:
        profile = get_object_or_404(CustomUser, pk=pk)
        profile.is_active = not profile.is_active
        profile.save()
        return JsonResponse({'success': True, 'new_status': profile.is_active, 'message': 'User status updated successfully.'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Profile not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

