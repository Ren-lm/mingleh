from django.urls import re_path
from . import consumers

#Code I wrote starts here

# This  contains the path for websocket communication.
# Whenever a connection request matches this path, it will be directed to ChatConsumer to handle the websocket connection.
websocket_urlpatterns = [
    re_path(r'ws/', consumers.ChatConsumer.as_asgi()) # re_path uses regular expression patterns to match URLs.
    # r'ws/' matches any URL that contains 'ws/' and directs it to the ChatConsumer for handling.
]

#Code I wrote ends here