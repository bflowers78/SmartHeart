from telebot import TeleBot
from telebot.types import Message
from loguru import logger
from app.bot.admin_handlers.states import AdminState, admin_contexts, mailing_contexts, MailingContext
from app.bot.messages import AdminMessages
from app.bot.services.file_service import create_file
from app.bot.services.mailing_service import create_mailing
from app.config import ADMIN_GROUP_ID, MAIN_TOPIC_ID, MAILING_TOPIC_ID


def register(bot: TeleBot) -> None:
    @bot.message_handler(func=lambda m: m.chat.id == ADMIN_GROUP_ID and m.message_thread_id == MAILING_TOPIC_ID, content_types=['text', 'photo', 'video'])
    def handle_mailing_message(message: Message) -> None:
        user_id = message.from_user.id
        
        message_type = message.content_type
        message_text = message.text or message.caption
        media_file_id = None
        
        if message_type == 'photo':
            media_file_id = message.photo[-1].file_id
        elif message_type == 'video':
            media_file_id = message.video.file_id
        
        mailing = create_mailing(
            message_type=message_type,
            message_text=message_text,
            media_file_id=media_file_id
        )
        
        ctx = MailingContext(
            mailing_id=mailing.id,
            message_id=message.message_id,
            message_type=message_type,
            message_text=message_text,
            media_file_id=media_file_id
        )
        mailing_contexts[user_id] = ctx
        
        send_methods = {
            'text': bot.send_message,
            'photo': bot.send_photo,
            'video': bot.send_video
        }
        
        send_params = {
            'text': {'text': message_text or "Текст не указан"},
            'photo': {'photo': media_file_id, 'caption': message_text},
            'video': {'video': media_file_id, 'caption': message_text}
        }
        
        method = send_methods.get(message_type, send_methods['text'])
        params = send_params.get(message_type, send_params['text'])
        
        sent_msg = method(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            reply_markup=AdminMessages.get_mailing_confirmation(mailing.id),
            **params
        )
        ctx.menu_message_id = sent_msg.message_id
    
    @bot.message_handler(func=lambda m: m.chat.id == ADMIN_GROUP_ID and m.message_thread_id == MAIN_TOPIC_ID, content_types=['text'])
    def handle_text_input(message: Message) -> None:
        
        user_id = message.from_user.id
        ctx = admin_contexts.get(user_id)
        
        if not ctx or not ctx.state:
            return
        
        if ctx.state == AdminState.FILLING_TITLE:
            ctx.title = message.text.strip()
            _update_menu(bot, message, ctx)
        elif ctx.state == AdminState.FILLING_MESSAGE_TEXT:
            ctx.message_text = message.text.strip()
            _update_menu(bot, message, ctx)
    
    @bot.message_handler(func=lambda m: m.chat.id == ADMIN_GROUP_ID and m.message_thread_id == MAIN_TOPIC_ID, content_types=['photo'])
    def handle_photo_input(message: Message) -> None:
        
        user_id = message.from_user.id
        ctx = admin_contexts.get(user_id)
        
        if not ctx or ctx.state != AdminState.FILLING_PHOTO:
            return
        
        ctx.media_file_id = message.photo[-1].file_id
        _update_menu(bot, message, ctx)
    
    @bot.message_handler(func=lambda m: m.chat.id == ADMIN_GROUP_ID and m.message_thread_id == MAIN_TOPIC_ID, content_types=['document'])
    def handle_document_input(message: Message) -> None:
        
        user_id = message.from_user.id
        ctx = admin_contexts.get(user_id)
        
        if not ctx or ctx.state != AdminState.FILLING_DOCUMENT:
            return
        
        file_name = message.document.file_name or "Без названия"
        file_extension = file_name.split('.')[-1] if '.' in file_name else None
        
        file_obj = create_file(
            file_name=file_name,
            file_extension=file_extension,
            file_id=message.document.file_id
        )
        
        ctx.document_file_ids.append(file_obj.id)
        _update_menu(bot, message, ctx)


def _update_menu(bot: TeleBot, message: Message, ctx) -> None:
    _delete_messages(bot, message.chat.id, message.message_id, ctx)
    
    if ctx.material_id:
        menu_data = AdminMessages.get_edit_material_menu(ctx)
    else:
        menu_data = AdminMessages.get_create_material_menu(ctx)
    
    bot.edit_message_text(
        message_id=ctx.menu_message_id,
        **menu_data
    )
    
    ctx.state = None


def _delete_messages(bot: TeleBot, chat_id: int, user_message_id: int, ctx) -> None:
    try:
        bot.delete_message(chat_id, user_message_id)
    except Exception:
        pass
    
    if ctx.request_message_id:
        try:
            bot.delete_message(chat_id, ctx.request_message_id)
            ctx.request_message_id = None
        except Exception:
            pass

