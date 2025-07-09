from django.urls import path
from . import views

# This is used to establish a namespce.
# Any path name that is defined here will be preappended by product_
# automatically by django if I want to referce this url it will be like thi
# {% url product:index %}

app_name = "consumer"

urlpatterns = [
    
    path("orderDetails/<int:pk>/", views.OrderDetails.as_view(), name="details"),
    path('orders/', views.ListOrderView.as_view(), name='list_orders'),
]
