# File: rackflow/dashboard/urls.py
from django.urls import path
from . import views
from .views import ListUsersView

app_name = "authentication"
urlpatterns = [
        path('add-employee/', views.Add_employee.as_view(), name='add_employee'),
        path('list_critical_products.html',views.is_critical, name='is_critical'),
        path('list_users/', views.ListUsersView.as_view(), name='list_users'),

]



