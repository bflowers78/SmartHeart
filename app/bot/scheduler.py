import threading
import time
from telebot import TeleBot
from loguru import logger
from app.bot.services import mailing_service
from app.bot.messages import AdminMessages
from app.bot.mailing_sender import send_mailing
from app.config import ADMIN_GROUP_ID, MAILING_TOPIC_ID


class MailingScheduler:
    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.running = False
        self.thread = None
    
    def start(self) -> None:
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Mailing scheduler started")
    
    def stop(self) -> None:
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Mailing scheduler stopped")
    
    def _run(self) -> None:
        while self.running:
            try:
                self._check_scheduled_mailings()
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
            
            time.sleep(60)
    
    def _check_scheduled_mailings(self) -> None:
        mailings = mailing_service.get_scheduled_mailings()
        
        for mailing in mailings:
            logger.info(f"Starting scheduled mailing {mailing.id}")
            self._send_mailing(mailing.id)
    
    def _send_mailing(self, mailing_id: int) -> None:
        mailing = mailing_service.get_mailing_by_id(mailing_id)
        users = mailing_service.get_active_users()
        total = len(users)
        
        send_methods = {
            'text': self.bot.send_message,
            'photo': self.bot.send_photo,
            'video': self.bot.send_video
        }
        
        send_params = {
            'text': {'text': mailing.message_text or "Текст не указан"},
            'photo': {'photo': mailing.media_file_id, 'caption': mailing.message_text},
            'video': {'video': mailing.media_file_id, 'caption': mailing.message_text}
        }
        
        method = send_methods.get(mailing.message_type, send_methods['text'])
        params = send_params.get(mailing.message_type, send_params['text'])
        
        progress_msg = method(
            chat_id=ADMIN_GROUP_ID,
            message_thread_id=MAILING_TOPIC_ID,
            reply_markup=AdminMessages.get_mailing_progress(mailing_id, total, 0, 0, 0),
            **params
        )
        
        def update_progress(total: int, sent: int, blocked: int, errors: int) -> None:
            try:
                self.bot.edit_message_reply_markup(
                    chat_id=ADMIN_GROUP_ID,
                    message_id=progress_msg.message_id,
                    reply_markup=AdminMessages.get_mailing_progress(mailing_id, total, sent, blocked, errors)
                )
            except Exception:
                pass
        
        send_mailing(self.bot, mailing_id, update_progress)
        
        mailing = mailing_service.get_mailing_by_id(mailing_id)
        self.bot.edit_message_reply_markup(
            chat_id=ADMIN_GROUP_ID,
            message_id=progress_msg.message_id,
            reply_markup=AdminMessages.get_mailing_completed(mailing, total)
        )

