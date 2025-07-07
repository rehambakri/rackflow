# File: rackflow/dashboard/urls.py
from django.urls import path
from . import views


urlpatterns = [
        path('add-employee/', views.add_employee, name='add_employee'),
]



