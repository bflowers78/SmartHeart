from telebot import TeleBot
from telebot.types import Message
from loguru import logger
from app.bot.messages import AdminMessages
from app.config import ADMIN_GROUP_ID, MAIN_TOPIC_ID


def register_admin_command_handlers(bot: TeleBot) -> None:
    @bot.message_handler(commands=["menu"])
    def handle_admin_menu(message: Message) -> None:
        if message.chat.id != ADMIN_GROUP_ID or message.message_thread_id != MAIN_TOPIC_ID:
            return

        bot.send_message(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            **AdminMessages.get_main_menu()
        )

