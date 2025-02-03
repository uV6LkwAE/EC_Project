
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from transactions.models import Message, Transaction

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ WebSocket 接続 """
        self.transaction_id = self.scope['url_route']['kwargs']['transaction_id']
        self.room_group_name = f'chat_{self.transaction_id}'

        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        self.channel_layer = get_channel_layer()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """ WebSocket 切断 """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """ WebSocket で受信したメッセージを処理 """
        data = json.loads(text_data)
        print(f"[Django] WebSocket 受信: {data}")

        if "message" in data:
            await self.process_message(data)
        elif "typing" in data:
            await self.send_typing_notification()
        elif "read" in data and "message_id" in data:
            await self.mark_message_as_read(data["message_id"])

    async def process_message(self, data):
        """ メッセージをデータベースに保存し、全クライアントに送信 """
        message_text = data["message"]
        sender = self.scope['user']
        transaction = await sync_to_async(Transaction.objects.get)(id=self.transaction_id)

        message = await sync_to_async(Message.objects.create)(
            content=message_text,
            sender=sender,
            transaction=transaction,
            timestamp=now(),
            is_read=False  # 受信側で未読の状態で保存
        )

        event_data = {
            "type": "chat_message",
            "message_id": message.id,
            "message": message_text,
            "sender": sender.username,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": message.is_read
        }

        print(f"[Django] `group_send()` 実行: {event_data}")
        await self.channel_layer.group_send(self.room_group_name, event_data)

    async def chat_message(self, event):
        """ 受信したメッセージをクライアントに送信し、受信者側で既読を更新 """
        print(f"[Django] クライアントへ送信: {event}")

        message_id = event["message_id"]
        await self.mark_message_as_read(message_id)

        await self.send(text_data=json.dumps(event))

    async def mark_message_as_read(self, message_id):
        """ 受信したメッセージを既読 (is_read=True) にし、送信者に通知 """
        message = await sync_to_async(Message.objects.get)(id=message_id)
        if not message.is_read:
            message.is_read = True
            await sync_to_async(message.save)()
            print(f"[Django] `is_read=True` に更新: message_id={message_id}")

            # 既読通知を送信者に送る
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "update_is_read",
                    "message_id": message.id
                }
            )

    async def update_is_read(self, event):
        """ 送信者に `✔ 既読` をリアルタイムで通知 """
        await self.send(text_data=json.dumps({
            "type": "update_is_read",
            "message_id": event["message_id"]
        }))

    async def send_typing_notification(self):
        """ 入力中の通知を全クライアントに送信 """
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_typing",
                "typing": True,
            }
        )

    async def chat_typing(self, event):
        """ 入力中の通知をクライアントに送信 """
        await self.send(text_data=json.dumps({
            "type": "typing",
            "typing": True,
        }))
