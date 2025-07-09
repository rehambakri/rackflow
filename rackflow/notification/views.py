from django.shortcuts import render
from django.views.generic import ListView

from .models import Notification


class NotificationList(ListView):
    model = Notification
    template_name = "notification/notifications.html"
    context_object_name = "notifications"
