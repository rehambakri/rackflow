from django.urls import path, re_path

from . import consumers

# the url is hardcoded like this websocket/ since our backend app doesn't
# care about any information coming from the front-end that's not already
# in the request/scope itself.
# our socket simply streams notifications to any remote socket it wants to connect to.
# of course we will deny any user that is not the manager from connect to this backend
# socket, since he is not authorized to see the notifications sent to the manager.
ASGI_urlpatterns = [path("notifications/websocket/", consumers.ChatConsumer.as_asgi())]
