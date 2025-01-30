
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from transactions.models import Message, Transaction

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.transaction_id = self.scope['url_route']['kwargs']['transaction_id']
        self.room_group_name = f'chat_{self.transaction_id}'

        # ユーザーが匿名の場合は接続を拒否
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return

        self.channel_layer = get_channel_layer()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """WebSocket で受信したメッセージを処理"""
        data = json.loads(text_data)
        print(f"📥 [Django] WebSocket 受信: {data}")  # 🔍 クライアントからのデータを表示

        # メッセージをデータベースに保存し、クライアントに送信
        if "message" in data:
            message_text = data["message"]
            sender = self.scope['user']
            transaction = await sync_to_async(Transaction.objects.get)(id=self.transaction_id)

            message = await sync_to_async(Message.objects.create)(
                content=message_text,
                sender=sender,
                transaction=transaction,
                timestamp=now()
            )

            event_data = {
                "type": "chat_message",
                "message_id": message.id,
                "message": message_text,
                "sender": sender.username,
                "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "reply_to": message.reply_to.content if message.reply_to else None,
                "is_read": message.is_read
            }

            print(f"📤 [Django] `group_send()` 実行: {event_data}")  # 🔍 `group_send()` の前にログ追加

            # 全クライアントにメッセージ送信（リアルタイム表示）
            print("メッセージを送信します。")
            await self.channel_layer.group_send(self.room_group_name, event_data)

        # `reaction` (リアクション) の処理
        elif "reaction" in data and "message_id" in data:
            message = await sync_to_async(Message.objects.get)(id=data["message_id"])
            await sync_to_async(message.reactions.update)({data["reaction"]: message.reactions.get(data["reaction"], 0) + 1})
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_reaction",
                    "reaction": data["reaction"],
                    "message_id": data["message_id"]
                }
            )

        # `typing` (入力中通知) の処理
        elif "typing" in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_typing",
                    "user": self.scope["user"].username if self.scope["user"].is_authenticated else "匿名"
                }
            )

        # `read` (既読通知) の処理
        elif "read" in data and "message_id" in data:
            message = await sync_to_async(Message.objects.get)(id=data["message_id"])
            if not message.is_read:
                message.is_read = True
                await sync_to_async(message.save)()

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_read",
                        "message_id": message.id
                    }
                )

    async def chat_message(self, event):
        """受信したメッセージをクライアントに送信"""
        print(f"📬 [Django] クライアントへ送信: {event}")  # 🔍 クライアントに送るデータを表示
        await self.send(text_data=json.dumps(event))

    async def chat_reaction(self, event):
        """リアクションをクライアントに送信"""
        await self.send(text_data=json.dumps({
            "reaction": event["reaction"],
            "message_id": event["message_id"]
        }))

    async def chat_typing(self, event):
        """入力中の通知をクライアントに送信"""
        await self.send(text_data=json.dumps({
            "typing": True,
            "user": event["user"]
        }))

    async def chat_read(self, event):
        """既読通知をクライアントに送信"""
        await self.send(text_data=json.dumps({
            "read": True,
            "message_id": event["message_id"]
        }))
