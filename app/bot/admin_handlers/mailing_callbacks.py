from datetime import datetime, timedelta
from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from app.bot.admin_handlers.states import mailing_contexts, MailingContext
from app.bot.messages import AdminMessages
from app.bot.services import mailing_service
from app.bot.mailing_sender import send_mailing
from app.config import ADMIN_GROUP_ID, moscow_now, MOSCOW_TZ


def register(bot: TeleBot) -> None:
    handlers = {
        'mail.schedule.': _show_calendar,
        'mail.cal.': _change_calendar_month,
        'mail.date.': _select_date,
        'mail.time.': _adjust_time,
        'mail.edit_time.': _edit_time,
        'mail.save_schedule.': _save_schedule,
        'mail.send_now.': _send_now,
        'mail.pause.': _pause_mailing,
        'mail.cancel.': _cancel_mailing,
    }
    
    @bot.callback_query_handler(func=lambda call: call.message.chat.id == ADMIN_GROUP_ID and call.data.startswith('mail.'))
    def handle_mailing_callback(call: CallbackQuery) -> None:
        logger.info(f"Mailing callback from {call.from_user.id}: {call.data}")
        bot.answer_callback_query(call.id)
        
        if call.data == 'mail.noop':
            return
        
        for prefix, handler in handlers.items():
            if call.data.startswith(prefix):
                handler(bot, call)
                break


def _show_calendar(bot: TeleBot, call: CallbackQuery) -> None:
    mailing_id = int(call.data.split('.')[-1])
    
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=AdminMessages.get_calendar_menu(mailing_id)
    )


def _change_calendar_month(bot: TeleBot, call: CallbackQuery) -> None:
    parts = call.data.split('.')
    mailing_id = int(parts[2])
    year = int(parts[3])
    month = int(parts[4])
    
    current_date = datetime(year, month, 1)
    
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=AdminMessages.get_calendar_menu(mailing_id, current_date)
    )


def _select_date(bot: TeleBot, call: CallbackQuery) -> None:
    parts = call.data.split('.')
    mailing_id = int(parts[2])
    year = int(parts[3])
    month = int(parts[4])
    day = int(parts[5])
    
    user_id = call.from_user.id
    
    if user_id not in mailing_contexts:
        mailing_contexts[user_id] = MailingContext(mailing_id=mailing_id)
    
    ctx = mailing_contexts[user_id]
    ctx.scheduled_date = datetime(year, month, day, tzinfo=MOSCOW_TZ)
    ctx.scheduled_time = moscow_now().replace(hour=12, minute=0, second=0, microsecond=0)
    ctx.menu_message_id = call.message.message_id
    
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=AdminMessages.get_time_menu(mailing_id, ctx)
    )


def _adjust_time(bot: TeleBot, call: CallbackQuery) -> None:
    parts = call.data.split('.')
    mailing_id = int(parts[2])
    minutes_delta = int(parts[3])
    
    user_id = call.from_user.id
    ctx = mailing_contexts.get(user_id)
    
    if not ctx:
        bot.answer_callback_query(call.id, "❌ Контекст не найден", show_alert=True)
        return
    
    if not ctx.scheduled_time:
        ctx.scheduled_time = moscow_now().replace(second=0, microsecond=0)
    
    ctx.scheduled_time += timedelta(minutes=minutes_delta)
    
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=AdminMessages.get_time_menu(mailing_id, ctx)
    )


def _edit_time(bot: TeleBot, call: CallbackQuery) -> None:
    mailing_id = int(call.data.split('.')[-1])
    user_id = call.from_user.id
    
    ctx = mailing_contexts.get(user_id)
    
    if not ctx:
        mailing = mailing_service.get_mailing_by_id(mailing_id)
        if not mailing:
            bot.answer_callback_query(call.id, "❌ Рассылка не найдена", show_alert=True)
            return
        
        ctx = MailingContext(mailing_id=mailing_id)
        if mailing.scheduled_at:
            ctx.scheduled_date = mailing.scheduled_at
            ctx.scheduled_time = mailing.scheduled_at
        ctx.menu_message_id = call.message.message_id
        mailing_contexts[user_id] = ctx
    
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=AdminMessages.get_time_menu(mailing_id, ctx)
    )


def _save_schedule(bot: TeleBot, call: CallbackQuery) -> None:
    mailing_id = int(call.data.split('.')[-1])
    user_id = call.from_user.id
    
    ctx = mailing_contexts.get(user_id)
    
    if not ctx or not ctx.scheduled_date or not ctx.scheduled_time:
        bot.answer_callback_query(call.id, "❌ Выберите дату и время", show_alert=True)
        return
    
    scheduled_datetime = ctx.scheduled_date.replace(
        hour=ctx.scheduled_time.hour,
        minute=ctx.scheduled_time.minute,
        second=0,
        microsecond=0
    )
    
    if scheduled_datetime < moscow_now():
        bot.answer_callback_query(call.id, "❌ Выбранное время уже прошло", show_alert=True)
        return
    
    mailing_service.update_mailing_schedule(mailing_id, scheduled_datetime)
    
    mailing = mailing_service.get_mailing_by_id(mailing_id)
    
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=AdminMessages.get_scheduled_mailing_info(mailing)
    )
    
    bot.answer_callback_query(call.id, "✅ Рассылка запланирована")


def _send_now(bot: TeleBot, call: CallbackQuery) -> None:
    mailing_id = int(call.data.split('.')[-1])
    users = mailing_service.get_active_users()
    total = len(users)
    
    user_id = call.message.chat.id
    ctx = mailing_contexts.get(user_id)
    if ctx:
        ctx.is_paused = False
    
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=AdminMessages.get_mailing_progress(mailing_id, total, 0, 0, 0)
    )
    
    def update_progress(total: int, sent: int, blocked: int, errors: int) -> None:
        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=AdminMessages.get_mailing_progress(mailing_id, total, sent, blocked, errors)
            )
        except Exception:
            pass
    
    def should_pause() -> bool:
        return ctx.is_paused if ctx else False
    
    sent, blocked, errors = send_mailing(bot, mailing_id, update_progress, should_pause)
    
    if ctx and ctx.is_paused:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(f'⏸ Приостановлено: {sent}/{total}', callback_data='mail.noop')
            )
        )
        return
    
    mailing = mailing_service.get_mailing_by_id(mailing_id)
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=AdminMessages.get_mailing_completed(mailing, total)
    )


def _pause_mailing(bot: TeleBot, call: CallbackQuery) -> None:
    mailing_id = int(call.data.split('.')[-1])
    user_id = call.from_user.id
    ctx = mailing_contexts.get(user_id)
    
    if ctx:
        ctx.is_paused = True
        mailing_service.update_mailing_status(mailing_id, "paused")
        bot.answer_callback_query(call.id, "⏸ Рассылка приостановлена")


def _cancel_mailing(bot: TeleBot, call: CallbackQuery) -> None:
    mailing_id = int(call.data.split('.')[-1])
    
    mailing_service.update_mailing_status(mailing_id, "cancelled")
    
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('❌ Рассылка отменена', callback_data='mail.noop')
        )
    )
    
    bot.answer_callback_query(call.id, "❌ Рассылка отменена")

