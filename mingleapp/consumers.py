import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from urllib.parse import parse_qs

# code I wrote starts here

class ChatConsumer(WebsocketConsumer):

    # This method is called when a websocket is handshaking / connecting.
    def connect(self):
        # Retrieving the user from the scope.
        self.user = self.scope["user"]

        # Parsing the query parameters from the scope to get the friend_id.
        query_params = parse_qs(self.scope['query_string'].decode())
        friend_id = query_params['chat'][0]

        # Constructing a unique room group name using the user and friend IDs.
        # The sorted function ensures the room name is consistent regardless of who connects first.
        group_name = 'room_' + '_'.join(sorted([str(self.user.id), str(friend_id)]))
        self.room_group_name = group_name

        # Adding the current channel to the group.
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        # Accepting the websocket connection.
        self.accept()

    # This method is called when the server receives a message from the client.
    def receive(self, text_data):
        # Converting the received text data into a JSON format.
        text_data_json = json.loads(text_data)

        # Extracting the 'message' key from the received data.
        message = text_data_json['message']

        # Debug prints for group name (can be removed in production).
        print('Group Name')
        print(self.room_group_name)

        # Sending the message to the group. All consumers that are a part of this group will receive this message.
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # This method is called when a chat_message type message is received from the group.
    def chat_message(self, event):
        # Extracting the 'message' key from the event.
        message = event['message']

        # Sending the message back to the client over the websocket in a JSON format.
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))
        # Code I wrote end here