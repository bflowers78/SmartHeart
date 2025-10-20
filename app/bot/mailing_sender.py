import time
from typing import Callable
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from loguru import logger
from app.bot.services import mailing_service


def send_mailing(
    bot: TeleBot,
    mailing_id: int,
    progress_callback: Callable[[int, int, int, int], None] | None = None,
    should_pause: Callable[[], bool] | None = None
) -> tuple[int, int, int]:
    mailing = mailing_service.get_mailing_by_id(mailing_id)
    if not mailing:
        return 0, 0, 0
    
    mailing_service.update_mailing_status(mailing_id, "sending")
    
    users = mailing_service.get_active_users()
    total = len(users)
    
    if total == 0:
        mailing_service.update_mailing_status(mailing_id, "completed")
        return 0, 0, 0
    
    sent_count = 0
    blocked_count = 0
    error_count = 0
    
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
    
    for i, user in enumerate(users):
        if should_pause and should_pause():
            mailing_service.update_mailing_stats(mailing_id, sent_count, blocked_count, error_count)
            return sent_count, blocked_count, error_count
        
        try:
            method(chat_id=user.user_id, **params)
            sent_count += 1
            
        except ApiTelegramException as e:
            if e.error_code == 403:
                mailing_service.block_user(user.user_id)
                blocked_count += 1
                logger.warning(f"User {user.user_id} blocked the bot")
            else:
                error_count += 1
                logger.error(f"Error sending to {user.user_id}: {e}")
        except Exception as e:
            error_count += 1
            logger.error(f"Unexpected error sending to {user.user_id}: {e}")
        
        if progress_callback and ((i + 1) % 10 == 0 or i == total - 1):
            progress_callback(total, sent_count, blocked_count, error_count)
        
        time.sleep(0.05)
    
    mailing_service.update_mailing_stats(mailing_id, sent_count, blocked_count, error_count)
    mailing_service.update_mailing_status(mailing_id, "completed")
    
    return sent_count, blocked_count, error_count

