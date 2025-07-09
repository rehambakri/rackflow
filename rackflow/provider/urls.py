from django.urls import path
from . import views

urlpatterns = [
    path('shipments/', views.ListShipmentView.as_view(), name='list_shipments'),
]
