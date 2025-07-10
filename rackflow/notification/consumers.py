import json

from asgiref.sync import async_to_sync
from authentication.models import CustomUser
from channels.generic.websocket import WebsocketConsumer

from .models import Notification


class ChatConsumer(WebsocketConsumer):
    # receive event, sent by the ASGI server when the remote socket
    # on the front-end want to connect
    def connect(self):
        # the consumer replies with an event to the ASGI server, telling
        # it to accept or close/refuse the incoming websocket connection.

        remote_user = self.scope.get("user")

        # if the remote user is not the manager, don't give it access to notification socket.
        # if the user is authenticated it can get notifications
        if remote_user.is_authenticated:
            # accept connection
            self.accept()

            # if it's the manager add the channel to the manager_notification_channels group
            if remote_user.is_staff:
                # add this channel to the manager channels "group" so that when
                # a view sends a notification (for example the create view of a product
                # that sends a notification that a product has been created), it can
                # easily send it to the group and all channels inside of this group will
                # get this message.
                # You may ask, why would be more than one manager channel streaming notification?
                # Imagine if the manager has the app open from different clients (chrome, firefox, phone)
                # each client has his own socket/channel that should receive notifications
                # from the backend. so the manager could have multiple channels running
                # at the same time, that's why we use group "manager_notification_channels".
                async_to_sync(self.channel_layer.group_add)(
                    "manager_notification_channels", self.channel_name
                )

            # if it's a regular user, create a group of channels with its id so that
            # the manager views can send it notifications
            else:
                async_to_sync(self.channel_layer.group_add)(
                    f"user_{remote_user.id}_notification_channels", self.channel_name
                )

        else:
            self.close(
                reason="You are not allowed to connect to a manager's streaming notification socket"
            )

        # on initial connection send all notifications of the connecting user to the front-end socket
        # so that it can manipluate the DOM and render all of these notifications
        notifications = Notification.objects.filter(receiver_id=remote_user.id).exclude(
            sender_id=remote_user.id
        )

        self.send_notifications(notifications)

    # receive event, sent by the ASGI server when the remote sockets
    # sends data
    # We won't really receive any data directly from the front-end client
    # since it's a notification app, we only want to stream data to it.
    # So we won't really do anything in this function.
    # We can leave it for now just in case we want to add more functionality later
    # like marking the notification as read and notifying the sender that the notification
    # has been seen by the receiver
    def receive(self, text_data):
        pass

    # this method accepts all events of type "notification.new" sent by any
    # other consumer or view
    def notification_new(self, event):
        # get the latest record of the notification table
        receiver_id = event.get("receiver_id")
        new_notification = (
            Notification.objects.filter(receiver_id=receiver_id)
            .exclude(sender_id=receiver_id)
            .last()
        )
        self.send_notifications([new_notification])

    # helper method to send data across the socket
    def send_notifications(self, notifications):
        # construct the message we will send to the socket
        for notif in notifications:
            if notif.type == "product_created":
                content = f'A new product "{notif.product.name}" was created by {notif.sender.first_name} {notif.sender.last_name} in the {notif.product.category.name} category'
            elif notif.type == "product_updated":
                content = f'product "{notif.product.name}" was updated by {notif.sender.first_name} {notif.sender.last_name}'
            elif notif.type == "product_deleted":
                content = f'product "{notif.product.name}" was deleted by {notif.sender.first_name} {notif.sender.last_name}'
            elif notif.type == "order_created":
                content = f'A new order to "{notif.order.consumer.name}" which has {notif.order.quantity} products was created by {notif.sender.first_name} {notif.sender.last_name}'
            elif notif.type == "shipment_created":
                content = f'A new shipment from "{notif.shipment.provider.name}" which has {notif.shipment.quantity} products was created by {notif.sender.first_name} {notif.sender.last_name}'
            elif notif.type == "order_accepted":
                content = f"Your order was accepted"
            elif notif.type == "order_rejected":
                content = f"Your order was rejected"
            elif notif.type == "shipment_accepted":
                content = f"Your sipment was accepted"
            elif notif.type == "shipment_rejected":
                content = f"Your shipment was rejected"

            notif._content = content

        # construct the entire array of notification objects we will send
        data = [
            {
                "type": n.type,
                "sender_id": n.sender.id,
                "receiver_id": n.receiver.id,
                "product_id": getattr(n.product, "id", None),
                "shipment_id": getattr(n.shipment, "id", None),
                "order_id": getattr(n.order, "id", None),
                "created_date_time": n.created_date_time.isoformat(),
                "content": getattr(n, "_content", ""),
            }
            for n in notifications
        ]

        # send it
        self.send(json.dumps(data))
