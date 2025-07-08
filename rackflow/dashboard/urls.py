# File: rackflow/dashboard/urls.py
from django.urls import path
from . import views


urlpatterns = [
        path('add-employee/', views.add_employee, name='add_employee'),
        path('list_critical_products.html',views.is_critical, name='is_critical'),

        
]



