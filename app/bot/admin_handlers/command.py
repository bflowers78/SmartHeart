from telebot import TeleBot
from telebot.types import Message
from loguru import logger
from app.bot.messages import AdminMessages
from app.bot.services.mailing_service import get_mailing_by_id
from app.bot.admin_handlers.states import mailing_contexts, MailingContext
from app.config import ADMIN_GROUP_ID, MAIN_TOPIC_ID, MAILING_TOPIC_ID


def register(bot: TeleBot) -> None:
    @bot.message_handler(commands=["menu"])
    def handle_admin_menu(message: Message) -> None:
        if message.chat.id != ADMIN_GROUP_ID or message.message_thread_id != MAIN_TOPIC_ID:
            return

        bot.send_message(
            message_thread_id=message.message_thread_id,
            **AdminMessages.get_main_menu()
            )
    
    @bot.message_handler(commands=["set"], func=lambda m: m.chat.id == ADMIN_GROUP_ID and m.message_thread_id == MAILING_TOPIC_ID)
    def handle_set_mailing(message: Message) -> None:
        try:
            command_parts = message.text.split('_')
            if len(command_parts) != 2:
                bot.reply_to(message, "❌ Используйте формат: /set_<id>")
                return
            
            mailing_id = int(command_parts[1])
            mailing = get_mailing_by_id(mailing_id)
            
            if not mailing:
                bot.reply_to(message, "❌ Рассылка не найдена")
                return
            
            user_id = message.from_user.id
            ctx = MailingContext(mailing_id=mailing_id)
            if mailing.scheduled_at:
                ctx.scheduled_date = mailing.scheduled_at
                ctx.scheduled_time = mailing.scheduled_at
            mailing_contexts[user_id] = ctx
            
            send_methods = {
                'text': bot.send_message,
                'photo': bot.send_photo,
                'video': bot.send_video
            }
            
            send_params = {
                'text': {'text': mailing.message_text or "Текст не указан"},
                'photo': {'photo': mailing.media_file_id, 'caption': mailing.message_text},
                'video': {'video': mailing.media_file_id, 'caption': mailing.message_text}
            }
            
            method = send_methods.get(mailing.message_type, send_methods['text'])
            params = send_params.get(mailing.message_type, send_params['text'])
            
            sent_msg = method(
                chat_id=message.chat.id,
                message_thread_id=message.message_thread_id,
                reply_markup=AdminMessages.get_scheduled_mailing_info(mailing),
                **params
            )
            ctx.menu_message_id = sent_msg.message_id
        except ValueError:
            bot.reply_to(message, "❌ Неверный формат ID")
        except Exception as e:
            logger.error(f"Error in set_mailing: {e}")
            bot.reply_to(message, "❌ Произошла ошибка")

