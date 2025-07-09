from django.urls import path

from . import views

app_name = "notification"
urlpatterns = [
    path("", views.NotificationList.as_view(), name="list"),
]
