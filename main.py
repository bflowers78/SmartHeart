from telebot import TeleBot
from loguru import logger
from app.config import BOT_TOKEN
from app.db.database import init_db
from app.bot.handlers.command import register_command_handlers
from app.bot.handlers.message import register_message_handlers
from app.bot.handlers.callback import register_callback_handlers

logger.add("logs/bot.log", rotation="10 MB", compression="zip", level="INFO")

bot = TeleBot(BOT_TOKEN)


def main() -> None:
    logger.info("Initializing database...")
    init_db()
    
    logger.info("Registering handlers...")
    register_command_handlers(bot)
    register_callback_handlers(bot)
    register_message_handlers(bot)
    
    logger.info("Bot started polling...")
    bot.infinity_polling()


if __name__ == "__main__":
    main()

