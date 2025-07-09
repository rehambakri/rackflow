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
        if not remote_user.is_staff:
            self.close(
                reason="You are not allowed to connect to a manager's streaming notification socket"
            )

        # accept connection
        self.accept()

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

        # on initial connection send all notifications to the front-end socket
        # so that it can manipluate the DOM and render all of these notifications
        notifications = Notification.objects.all()
        data = [
            {
                "id": n.id,
                "type": n.type,
                "content": n.content,
                "created": n.created_date_time.isoformat(),
                # optional: stringify user
                "to_who": str(n.to_who),
            }
            for n in notifications
        ]

        # here I'm specifiying a type so that the fron-end socket can
        # distinguish between receiving an entire list of notifications when first
        # connecting, and when it receives a single notification later on
        self.send(json.dumps({"type": "notification_list", "notifications": data}))

    def receive(self, text_data):
        pass
