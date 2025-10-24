from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from app.bot.messages import Messages, AdminMessages
from app.bot.services import material_service, user_service, file_service
from app.bot.services.amocrm_service import create_lead, add_note_to_lead
from app.bot.user_handlers.states import UserState, user_contexts, UserContext
from app.db.models import Material, User

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

def register(bot: TeleBot) -> None:
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call: CallbackQuery) -> None:
        logger.info(f"Callback from {call.from_user.id}: {call.data}")
        
        if call.data in MENU_MESSAGES:
            _menu_navigation(bot, call)
        elif call.data.startswith('back_to.'):
            _back_prevmenu(bot, call)
        elif call.data.startswith('get_material.'):
            if _is_complete_profile(bot, call, 'material'):
                _display_material(bot, call)
        elif call.data.startswith('fill.'):
            _handle_profile_fill(bot, call)
        elif call.data == 'save_data':
            _handle_save_profile(bot, call)
        elif call.data == 'accept_consent':
            _handle_consent_acceptance(bot, call)
        elif call.data in ('become_participant', 'become_viewer'):
            if _is_complete_profile(bot, call, 'roasting'):
                _handle_roasting_request(bot, call)

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


def _is_complete_profile(bot: TeleBot, call: CallbackQuery, action_type: str) -> bool:
    """Проверяет готовность профиля для указанного действия"""
    user = user_service.get_user_by_user_id(call.from_user.id)
    
    if not user or not user.is_consent_given:
        _show_consent_message(bot, call, action_type)
        return False
    
    if not user.is_profile_completed:
        user_id = call.from_user.id
        
        if user_id not in user_contexts:
            user_contexts[user_id] = UserContext()
        
        ctx = user_contexts[user_id]
        
        # Сохраняем ожидающее действие в зависимости от типа
        if action_type == 'material':
            material_id = int(call.data.split('.')[-1])
            ctx.pending_material_id = material_id
        elif action_type == 'roasting':
            ctx.pending_roasting_request = call.data
        
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

def _show_consent_message(bot: TeleBot, call: CallbackQuery, action_type: str) -> None:
    """Показывает сообщение с согласием на обработку персональных данных"""
    user_id = call.from_user.id
    
    if user_id not in user_contexts:
        user_contexts[user_id] = UserContext()
    
    ctx = user_contexts[user_id]
    
    if action_type == 'material':
        material_id = int(call.data.split('.')[-1])
        ctx.pending_material_id = material_id
    elif action_type == 'roasting':
        ctx.pending_roasting_request = call.data
    
    ctx.state = UserState.CONSENT_REQUESTED
    ctx.consent_message_id = call.message.message_id
    
    consent_data = Messages.get_consent_message()
    
    msg = bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        **consent_data
    )
    ctx.consent_message_id = msg.message_id

def _handle_consent_acceptance(bot: TeleBot, call: CallbackQuery) -> None:
    """Обрабатывает принятие согласия на обработку персональных данных"""
    user_id = call.from_user.id
    user = user_service.get_user_by_user_id(user_id)
    
    if not user:
        user = user_service.create_user(call.from_user)
    
    user_service.update_user_consent(user_id, True)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    ctx = user_contexts.get(user_id)
    if ctx and (ctx.pending_material_id or ctx.pending_roasting_request):
        ctx.state = UserState.MATERIAL_REQUESTED
        
        msg = bot.send_message(call.message.chat.id, **Messages.get_profile_fill_menu(user))
        ctx.profile_menu_message_id = msg.message_id

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
    user = user_service.get_user_by_user_id(user_id)
    
    if not user.is_profile_completed:
        bot.answer_callback_query(call.id, "❌ Заполнены не все поля", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "✅ Данные успешно сохранены")
    bot.send_message(**AdminMessages.profile_completed(user))
    
    _create_user_lead_with_contacts(user)
    
    ctx = user_contexts.get(user_id)
    if ctx and ctx.pending_material_id:
        call.data = f'get_material.{ctx.pending_material_id}'
        _display_material(bot, call)
        ctx.pending_material_id = None
        ctx.state = None
    elif ctx and ctx.pending_roasting_request:
        call.data = ctx.pending_roasting_request
        _handle_roasting_request(bot, call)
        ctx.pending_roasting_request = None
        ctx.state = None


def _create_user_lead_with_contacts(user: User) -> None:
    """Создает сделку в AMO CRM с контактными данными пользователя"""
    lead_name = user.full_name
    lead_id = create_lead(lead_name)
    
    if lead_id:
        user_service.update_user_lead_id(user.user_id, lead_id)
        logger.info(f"Создана сделка {lead_id} для пользователя {user.user_id}")
        
        # Отправляем примечание с контактными данными
        contact_info = _get_user_contact_info(user)
        add_note_to_lead(lead_id, "\n".join(contact_info))
        logger.info(f"Добавлено примечание к сделке {lead_id} с контактными данными")


def _get_user_contact_info(user: User) -> list[str]:
    """Формирует список контактной информации пользователя"""
    contact_info = [
        f"ФИО: {user.full_name}",
        f"Компания: {user.company}",
        f"Должность: {user.position}",
        f"Телефон: {user.phone_number}"
    ]
    
    if user.username:
        contact_info.append(f"Username: @{user.username}")
    
    return contact_info


def _create_lead_with_note(user: User, lead_name: str, note_parts: list[str]) -> None:
    """Создает сделку в AMO CRM и добавляет к ней примечание"""
    lead_id = create_lead(lead_name)
    
    if not lead_id:
        logger.error(f"Не удалось создать сделку для пользователя {user.user_id}")
        return
    
    add_note_to_lead(lead_id, "\n".join(note_parts))


def _display_material(bot: TeleBot, call: CallbackQuery) -> None:
    material_id = int(call.data.split('.')[-1])
    material = material_service.get_material_by_id(material_id)
    user = user_service.get_user_by_user_id(call.from_user.id)
    
    material_service.record_material_view(call.from_user.id, material_id)
    bot.send_message(**AdminMessages.material_interest(call.from_user.id, call.from_user.username, material))
    
    if user and user.lead_id:
        note_text = f"Просмотрен материал: {material.title}"
        add_note_to_lead(user.lead_id, note_text)
        logger.info(f"Добавлено примечание к сделке {user.lead_id}: {note_text}")
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    sent_messages = send_material_content(bot, call.message.chat.id, material)
    user_messages[call.from_user.id] = sent_messages

def send_material_content(bot: TeleBot, chat_id: int, material: Material) -> list[int]:
    sent_messages = []
    category_menu = CATEGORY_MENU_MAP.get(material.category, 'main_menu')
    back_markup = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙 Назад', callback_data=f'back_to.{category_menu}'))
    has_documents = material.document_file_ids and len(material.document_file_ids) > 0
    first_msg_markup = None if has_documents else back_markup

    if material.media_file_id and len(material.message_text) > 1024:
        photo_msg = bot.send_photo(chat_id, material.media_file_id)
        sent_messages.append(photo_msg.message_id)
        msg = bot.send_message(chat_id, material.message_text, reply_markup=first_msg_markup)
    elif material.media_file_id:
        msg = bot.send_photo(chat_id, material.media_file_id, caption=material.message_text, reply_markup=first_msg_markup)
    else:
        msg = bot.send_message(chat_id, material.message_text, reply_markup=first_msg_markup)

    sent_messages.append(msg.message_id)
    
    if has_documents:
        files = file_service.get_files_by_ids(material.document_file_ids)
        for i, file in enumerate(files):
            is_last = i == len(files) - 1
            markup = back_markup if is_last else None
            msg = bot.send_document(chat_id, file.file_id, reply_markup=markup)
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


def _handle_roasting_request(bot: TeleBot, call: CallbackQuery) -> None:
    user = user_service.get_user_by_user_id(call.from_user.id)
    request_type = "participant" if call.data == 'become_participant' else "viewer"
    request_type_ru = "участником" if call.data == 'become_participant' else "зрителем"
    
    bot.send_message(**AdminMessages.roasting_request(user, request_type))
    
    # Добавляем примечание к сделке
    if user and user.lead_id:
        note_text = f"Подана заявка стать {request_type_ru}"
        add_note_to_lead(user.lead_id, note_text)
        logger.info(f"Добавлено примечание к сделке {user.lead_id}: {note_text}")
    
    bot.answer_callback_query(call.id, "✅ Ваша заявка принята!", show_alert=True)
    bot.send_message(
        call.message.chat.id,
        "🎉 *Спасибо за вашу активность!*\n\n"
        "Ваша заявка принята. В ближайшее время мы свяжемся с вами.",
        parse_mode='Markdown'
    )