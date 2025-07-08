# File: rackflow/dashboard/urls.py
from django.urls import path
from . import views


urlpatterns = [
        path('add-employee/', views.Add_employee.as_view(), name='add_employee'),
]



