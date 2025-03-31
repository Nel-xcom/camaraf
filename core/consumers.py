import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Mensaje, CustomUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = f"chat_{self.scope['url_route']['kwargs']['usuario_id']}"
        self.room_group_name = f"chat_{self.room_name}"

        # Añadir al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quitar del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibir mensaje del WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        contenido = data['contenido']
        destinatario_id = data['destinatario_id']
        remitente_id = self.scope['user'].id

        # Guardar el mensaje en la base de datos
        await self.save_message(remitente_id, destinatario_id, contenido)

        # Enviar mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'remitente': self.scope['user'].username,
                'contenido': contenido,
                'fecha_envio': data['fecha_envio']
            }
        )

    # Recibir mensaje del grupo
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, remitente_id, destinatario_id, contenido):
        remitente = CustomUser.objects.get(id=remitente_id)
        destinatario = CustomUser.objects.get(id=destinatario_id)
        Mensaje.objects.create(remitente=remitente, destinatario=destinatario, contenido=contenido)
