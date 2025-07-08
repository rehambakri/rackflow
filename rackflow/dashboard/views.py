from django.shortcuts import render
from authentication.forms import CustomUserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy

# Create your views here.




class Add_employee(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('porduct:list')
    template_name = 'add_employee.html'
