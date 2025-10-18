from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from app.bot.messages import Messages
from app.bot.services.material_service import get_material_by_id
from app.db.models import Material

user_messages: dict[int, list[int]] = {}

CATEGORY_MENU_MAP = {
    'product': 'products',
    'helpful': 'materials',
    'roasting': 'roasting'
}

MENU_MESSAGES = {
    'main_menu': Messages.get_main_menu,
    'products': Messages.get_products_menu,
    'materials': Messages.get_materials_menu,
    'roasting': Messages.get_roasting_menu,
    'about': Messages.get_about_menu
}

def register_callback_handlers(bot: TeleBot) -> None:
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call: CallbackQuery) -> None:
        logger.info(f"Callback from {call.from_user.id}: {call.data}")
        bot.answer_callback_query(call.id)
        
        if call.data in MENU_MESSAGES:
            _menu_navigation(bot, call)
        elif call.data.startswith('back_to.'):
            _back_prevmenu(bot, call)
        elif call.data.startswith('get_material.'):
            _display_material(bot, call)

def _menu_navigation(bot: TeleBot, call: CallbackQuery) -> None:
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        **MENU_MESSAGES[call.data]()
    )


def _back_prevmenu(bot: TeleBot, call: CallbackQuery) -> None:
    delete_user_messages(bot, call.message.chat.id, call.from_user.id)
    bot.send_message(call.message.chat.id, **MENU_MESSAGES[call.data]())


def _display_material(bot: TeleBot, call: CallbackQuery) -> None:
    material_id = int(call.data.split('.')[-1])
    material = get_material_by_id(material_id)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    sent_messages = send_material_content(bot, call.message.chat.id, material)
    user_messages[call.from_user.id] = sent_messages

def send_material_content(bot: TeleBot, chat_id: int, material: Material) -> list[int]:
    sent_messages = []
    category_menu = CATEGORY_MENU_MAP.get(material.category, 'main_menu')
    back_markup = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data=f'back_to.{category_menu}'))
    has_documents = material.document_file_ids and len(material.document_file_ids) > 0
    first_msg_markup = None if has_documents else back_markup
    
    if material.media_file_id:
        msg = bot.send_photo(chat_id, material.media_file_id, caption=material.message_text, reply_markup=first_msg_markup)
    else:
        msg = bot.send_message(chat_id, material.message_text, reply_markup=first_msg_markup)

    sent_messages.append(msg.message_id)
    
    if has_documents:
        for i, file_id in enumerate(material.document_file_ids):
            is_last = i == len(material.document_file_ids) - 1
            markup = back_markup if is_last else None
            msg = bot.send_document(chat_id, file_id, reply_markup=markup)
            sent_messages.append(msg.message_id)
    
    return sent_messages

def delete_user_messages(bot: TeleBot, chat_id: int, user_id: int) -> None:
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                logger.error(f"Failed to delete message {msg_id}: {e}")
        del user_messages[user_id]