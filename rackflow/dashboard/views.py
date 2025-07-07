from django.shortcuts import render

# Create your views here.



def add_employee(request):
        return render(request, 'add_employee.html')