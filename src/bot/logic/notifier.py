import telegram

from core.models import User, Tenant
from asgiref.sync import async_to_sync


class TelegramBotNotifier:
    def __init__(self, tenant: Tenant):
        self.bot = telegram.Bot(token=tenant.telegram_bot_token)

    @async_to_sync
    async def notify(self, user: User, message: str):
        if not user.telegram_id:
            return
        await self.bot.send_message(chat_id=user.telegram_id, text=message)
