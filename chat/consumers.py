# chat/consumers.py

import gc
import random

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        content = await self.decode_json(text_data)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "content": content}
        )

        for i in range(500):
            # Create a struct of variable Mb from 1 to 5
            struct = bytearray(1024 * 1024 * random.randint(1, 5))
            message = bytes(struct)
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.binary", "message": message}
            )

            print(f"Sent message {i + 1} of 500")

            del struct
            gc.collect()

    # Receive message from room group
    async def chat_message(self, event):
        content = event["content"]

        # Send message to WebSocket
        await self.send_json(content=content)

    async def chat_binary(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(bytes_data=message)
