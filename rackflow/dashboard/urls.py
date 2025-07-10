# File: rackflow/dashboard/urls.py
from django.urls import path
from . import views 
from .views import  toggle_user_status , ListUsersView 

app_name = "authentication"
urlpatterns = [
        path('add-employee/', views.Add_employee.as_view(), name='add_employee'),
        path('list_critical_products',views.is_critical, name='is_critical'),
        path('update-user-profile/<int:pk>/', views.UpdateEmployeeProfileView.as_view(), name='update_user_profile'),
        path('profile/<int:pk>/toggle_status/', toggle_user_status, name='toggle_user_status'),
        path('list_users/', views.ListUsersView.as_view(), name='list_users'),




