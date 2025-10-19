from telebot import TeleBot
from telebot.types import Message
from app.bot.services.user_service import create_user
from app.bot.messages import Messages as Msg, AdminMessages


def register_command_handlers(bot: TeleBot) -> None:
    @bot.message_handler(commands=["start", "menu"])
    def handle_start(message: Message) -> None:
        is_new = create_user(message.from_user)
        
        if is_new:
            bot.send_message(**AdminMessages.new_user(message.from_user))
        
        bot.send_message(
            chat_id=message.chat.id,
            **Msg.get_main_menu()
        )



