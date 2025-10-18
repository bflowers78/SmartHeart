from telebot import TeleBot
from telebot.types import Message
from loguru import logger


def register_message_handlers(bot: TeleBot) -> None:
    @bot.message_handler(content_types=["text"])
    def handle_text(message: Message) -> None:
        logger.info(f"Received message from {message.from_user.id}: {message.text}")
        bot.send_message(
            message.chat.id,
            f"Вы написали: {message.text}"
        )

