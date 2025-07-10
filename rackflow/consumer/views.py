from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from notification.models import Notification
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response

from .models import Order


class OrderDetails(DetailView):
    model = Order
    template_name = "consumer/orderDetails.html"
    context_object_name = "order"


class ListOrderView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "consumer/list_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(user=user)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_order_status(request, id):
    # check if user is a manager
    manager = request.user
    if not manager.is_staff:  # change to custom check if needed
        return Response(
            {"detail": "Only managers can update order status."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # get the order
    order = get_object_or_404(Order, id=id)

    # only allow status update if it's currently pending
    if order.status != "pending":
        return Response(
            {"detail": "Order status cannot be updated."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # update status (e.g., to accepted)
    new_status = request.data.get("status", "").lower()
    if new_status not in [
        "accepted",
        "rejected",
    ]:  # or whatever your allowed values are
        return Response(
            {"detail": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    order.status = new_status
    order.a_date = datetime.now()
    order.save()

    # send notification to the user who created the order
    Notification.objects.create(
        sender=manager,
        receiver=order.user,
        order=order,
        type="order_accepted" if new_status == "accepted" else "order_rejected",
    )

    # send websocket notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{order.user.id}_notification_channels",
        {
            "type": "notification.new",
            "receiver_id": order.user.id,
        },
    )
    return Response({"detail": f"Order status updated to {new_status}."})
