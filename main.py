from telebot import TeleBot
from loguru import logger
from app.config import BOT_TOKEN
from app.db.database import init_db
from app.bot import user_handlers, admin_handlers
from app.bot.scheduler import MailingScheduler

logger.add("logs/bot.log", rotation="10 MB", compression="zip", level="INFO")

bot = TeleBot(BOT_TOKEN)


def main() -> None:
    logger.info("Initializing database...")
    init_db()

    logger.info("Registering admin handlers...")
    admin_handlers.command.register(bot)
    admin_handlers.callback.register(bot)
    admin_handlers.mailing_callbacks.register(bot)
    admin_handlers.message.register(bot)
    
    logger.info("Registering user handlers...")
    user_handlers.command.register(bot)
    user_handlers.callback.register(bot)
    user_handlers.message.register(bot)
    
    logger.info("Starting mailing scheduler...")
    scheduler = MailingScheduler(bot)
    scheduler.start()
    
    logger.info("Bot started polling...")
    bot.infinity_polling()


if __name__ == "__main__":
    main()

