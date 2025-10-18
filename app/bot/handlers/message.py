from telebot import TeleBot
from telebot.types import Message
from loguru import logger
from app.bot.services.user_service import get_user_by_user_id, update_user_profile
from app.bot.states import UserState, user_contexts, UserContext
from app.bot.validators import validate_full_name, validate_company, validate_position, validate_phone
from app.bot.messages import Messages

FIELD_VALIDATORS = {
    UserState.FILLING_FULL_NAME: ('full_name', validate_full_name),
    UserState.FILLING_COMPANY: ('company', validate_company),
    UserState.FILLING_POSITION: ('position', validate_position),
    UserState.FILLING_PHONE: ('phone_number', validate_phone)
}


def register_message_handlers(bot: TeleBot) -> None:
    @bot.message_handler(content_types=["text"])
    def handle_text(message: Message) -> None:
        logger.info(f"Received message from {message.from_user.id}: {message.text}")
        
        user_id = message.from_user.id
        ctx = user_contexts.get(user_id)
        
        if ctx and ctx.state in FIELD_VALIDATORS:
            _process_profile_field(bot, message, ctx)


def _process_profile_field(bot: TeleBot, message: Message, ctx: UserContext) -> None:
    """Обрабатывает ввод данных профиля"""
    field_name, validator = FIELD_VALIDATORS[ctx.state]
    is_valid, error = validator(message.text)
    
    if is_valid:
        update_user_profile(message.chat.id, field_name, message.text.strip())
        _show_profile_menu(bot, message, ctx)
    else:
        bot.send_message(message.chat.id, f"❌ {error}")


def _show_profile_menu(bot: TeleBot, message: Message, ctx: UserContext) -> None:
    """Показывает обновленное меню профиля после заполнения поля"""
    user_id = message.chat.id
    
    _delete_messages(bot, user_id, message.message_id, ctx)
    
    user = get_user_by_user_id(user_id)
    menu_data = Messages.get_profile_fill_menu(user)
    
    bot.edit_message_text(chat_id=user_id, message_id=ctx.profile_menu_message_id, **menu_data)


def _delete_messages(bot: TeleBot, user_id: int, user_message_id: int, ctx: UserContext) -> None:
    """Удаляет сообщения пользователя и запроса"""
    try:
        bot.delete_message(user_id, user_message_id)
    except Exception:
        pass
    
    if ctx.request_message_id:
        try:
            bot.delete_message(user_id, ctx.request_message_id)
            ctx.request_message_id = None
        except Exception:
            pass

