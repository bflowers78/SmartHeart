from telebot import TeleBot
from loguru import logger
from app.config import BOT_TOKEN
from app.db.database import init_db
from app.bot.user_handlers.command import register_command_handlers
from app.bot.user_handlers.message import register_message_handlers
from app.bot.user_handlers.callback import register_callback_handlers
from app.bot.admin_handlers.command import register_admin_command_handlers
from app.bot.admin_handlers.message import register_admin_message_handlers
from app.bot.admin_handlers.callback import register_admin_callback_handlers

logger.add("logs/bot.log", rotation="10 MB", compression="zip", level="INFO")

bot = TeleBot(BOT_TOKEN)


def main() -> None:
    logger.info("Initializing database...")
    init_db()

    logger.info("Registering admin handlers...")
    register_admin_command_handlers(bot)
    register_admin_callback_handlers(bot)
    register_admin_message_handlers(bot)
    
    logger.info("Registering handlers...")
    register_command_handlers(bot)
    register_callback_handlers(bot)
    register_message_handlers(bot)
    
    
    logger.info("Bot started polling...")
    bot.infinity_polling()


if __name__ == "__main__":
    main()

