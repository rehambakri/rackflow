from django.urls import path
from . import views

# This is used to establish a namespce.
# Any path name that is defined here will be preappended by product_
# automatically by django if I want to referce this url it will be like thi
# {% url product:index %}


app_name = "provider"

urlpatterns = [ 
    path("shipmentDetails/<int:pk>/", views.ShipmentDetails.as_view(), name="details"),
    path('shipments/', views.ListShipmentView.as_view(), name='list_shipments'),
    path('shipment/create/', views.ShipmentCreateView.as_view(), name='create_shipment'),
    path('shipment/update/<int:pk>/', views.ShipmentUpdateView.as_view(), name='update_shipment'),
    path("api/shipment/<int:id>/status/", views.update_shipment_status),
    path('shipments/<int:pk>/process-arrival/', 
         views.ShipmentArrivalView.as_view(), 
         name='process_arrival'),


]
