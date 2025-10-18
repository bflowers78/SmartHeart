from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from app.bot.messages import Messages
from app.bot.services.material_service import get_material_by_id
from app.bot.services.user_service import get_user_by_user_id
from app.bot.states import UserState, user_contexts, UserContext
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

FIELD_PROMPTS = {
    'full_name': (UserState.FILLING_FULL_NAME, "📝 Введите ваше ФИО:"),
    'company': (UserState.FILLING_COMPANY, "🏢 Введите название компании:"),
    'position': (UserState.FILLING_POSITION, "💼 Введите вашу должность:"),
    'phone': (UserState.FILLING_PHONE, "📞 Введите номер телефона:")
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
            if _is_complete_profile(bot, call):
                _display_material(bot, call)
        elif call.data.startswith('fill.'):
            _handle_profile_fill(bot, call)
        elif call.data == 'save_data':
            _handle_save_profile(bot, call)

def _menu_navigation(bot: TeleBot, call: CallbackQuery) -> None:
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        **MENU_MESSAGES[call.data]()
    )


def _back_prevmenu(bot: TeleBot, call: CallbackQuery) -> None:
    category_menu = call.data.split('.')[-1]
    delete_user_messages(bot, call.message.chat.id, call.from_user.id)
    bot.send_message(call.message.chat.id, **MENU_MESSAGES[category_menu]())


def _is_complete_profile(bot: TeleBot, call: CallbackQuery) -> None:
    material_id = int(call.data.split('.')[-1])
    user = get_user_by_user_id(call.from_user.id)
    
    if not user or not user.is_profile_completed:
        user_id = call.from_user.id
        
        if user_id not in user_contexts:
            user_contexts[user_id] = UserContext()
        
        ctx = user_contexts[user_id]
        ctx.pending_material_id = material_id
        ctx.state = UserState.MATERIAL_REQUESTED
        ctx.profile_menu_message_id = call.message.message_id
        
        menu_data = Messages.get_profile_fill_menu(user)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            **menu_data
        )
                
        return False
    return True

def _handle_profile_fill(bot: TeleBot, call: CallbackQuery) -> None:
    field = call.data.split('.')[-1]
    user_id = call.from_user.id
    
    if user_id not in user_contexts:
        user_contexts[user_id] = UserContext()
    
    ctx = user_contexts[user_id]
    ctx.profile_menu_message_id = call.message.message_id
    
    state, prompt = FIELD_PROMPTS[field]
    ctx.state = state
    msg = bot.send_message(call.message.chat.id, prompt)
    ctx.request_message_id = msg.message_id


def _handle_save_profile(bot: TeleBot, call: CallbackQuery) -> None:
    """Обработка кнопки 'Сохранить' - проверяет заполненность профиля"""
    user_id = call.from_user.id
    user = get_user_by_user_id(user_id)
    
    if not user.full_name or not user.company or not user.position or not user.phone_number:
        bot.answer_callback_query(call.id, "❌ Заполнены не все поля", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "✅ Данные успешно сохранены")
    
    ctx = user_contexts.get(user_id)
    if ctx and ctx.pending_material_id:
        call.data = f'get_material.{ctx.pending_material_id}'
        _display_material(bot, call)
        ctx.pending_material_id = None
        ctx.state = None


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