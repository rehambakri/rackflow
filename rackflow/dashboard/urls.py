# File: rackflow/dashboard/urls.py
from django.urls import path
from . import views


urlpatterns = [
        path('add-employee/', views.Add_employee.as_view(), name='add_employee'),
        path('list_critical_products',views.is_critical, name='is_critical'),
         path('update-user-profile/<int:pk>/', views.UpdateEmployeeProfileView.as_view(), name='update_user_profile'), ]



