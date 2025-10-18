from telebot import TeleBot
from telebot.types import Message
from loguru import logger
from app.bot.services.user_service import create_user
from app.bot.messages import Messages as Msg


def register_command_handlers(bot: TeleBot) -> None:
    @bot.message_handler(commands=["start", "menu"])
    def handle_start(message: Message) -> None:
        create_user(message.from_user)
        logger.info(f"User {message.chat.id} started the bot")
        
        bot.send_message(
            chat_id=message.chat.id,
            **Msg.get_main_menu()
        )



