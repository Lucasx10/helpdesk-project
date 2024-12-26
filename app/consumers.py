import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChamadoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Adiciona o usuário ao grupo chamado "chamados"
        self.group_name = 'chamados'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove o usuário do grupo "chamados"
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Método para tratar mensagens recebidas via WebSocket
        data = json.loads(text_data)
        # Envia uma mensagem de notificação para o grupo "chamados"
        await self.channel_layer.group_send(self.group_name, {
            'type': 'send_update',
            'message': data['message'],  # A mensagem do WebSocket
        })

    async def send_update(self, event):
        # Envia mensagem para o WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
