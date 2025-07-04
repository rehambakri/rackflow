from django.urls import path

from . import views

# This is used to establish a namespce.
# Any path name that is defined here will be preappended by product_
# automatically by django if I want to referce this url it will be like thi
# {% url product:index %}
app_name = "product"
urlpatterns = [
    path("", views.ProductList.as_view(), name="list"),
    path("create", views.ProductCreate.as_view(), name="create"),
]
