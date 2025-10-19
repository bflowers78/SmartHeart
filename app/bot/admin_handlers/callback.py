from datetime import datetime
from telebot import TeleBot
from telebot.types import CallbackQuery, InputFile
from loguru import logger
from app.bot.admin_handlers.states import AdminState, admin_contexts, AdminContext
from app.bot.messages import AdminMessages
from app.bot.services.material_service import get_material_by_id, create_material, update_material, delete_material, get_material_statistics
from app.bot.services.user_service import get_all_users_with_materials
from app.bot.services.file_service import delete_file
from app.bot.utils import create_statistics_excel, create_users_excel
from app.config import ADMIN_GROUP_ID


CATEGORY_MAP = {
    '💡 Продукты': 'product',
    '📕 Полезные материалы': 'helpful',
    '🔥 Прожарка': 'roasting'
}


def register_admin_callback_handlers(bot: TeleBot) -> None:
    @bot.callback_query_handler(func=lambda call: call.data.startswith('admin.'))
    def handle_admin_callback(call: CallbackQuery) -> None:
        if call.message.chat.id != ADMIN_GROUP_ID:
            return
        
        logger.info(f"Admin callback from {call.from_user.id}: {call.data}")
        bot.answer_callback_query(call.id)
        
        if call.data == 'admin.main':
            _show_main_menu(bot, call)
        elif call.data == 'admin.users':
            _export_users(bot, call)
        elif call.data.startswith('admin.category.'):
            _show_category_menu(bot, call)
        elif call.data.startswith('admin.add.'):
            _start_create_material(bot, call)
        elif call.data.startswith('admin.material.'):
            _show_material(bot, call)
        elif call.data.startswith('admin.fill.'):
            _handle_fill_field(bot, call)
        elif call.data.startswith('admin.edit.'):
            _handle_edit_field(bot, call)
        elif call.data.startswith('admin.edit_start.'):
            _start_edit_material(bot, call)
        elif call.data == 'admin.publish':
            _publish_material(bot, call)
        elif call.data == 'admin.save':
            _save_material(bot, call)
        elif call.data.startswith('admin.delete_file.'):
            _delete_file_from_material(bot, call)
        elif call.data.startswith('admin.delete_confirm.'):
            _confirm_delete(bot, call)
        elif call.data.startswith('admin.delete.'):
            _delete_material(bot, call)
        elif call.data.startswith('admin.stats.'):
            _send_material_statistics(bot, call)


def _show_main_menu(bot: TeleBot, call: CallbackQuery) -> None:
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_main_menu()
        )


def _show_category_menu(bot: TeleBot, call: CallbackQuery) -> None:
    category = call.data.split('.')[-1]
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_category_menu(category)
        )


def _start_create_material(bot: TeleBot, call: CallbackQuery) -> None:
    category = call.data.split('.')[-1]
    user_id = call.from_user.id
    
    admin_contexts[user_id] = AdminContext(category=category)
    ctx = admin_contexts[user_id]
    ctx.menu_message_id = call.message.message_id
    
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_create_material_menu(ctx)
        )


def _show_material(bot: TeleBot, call: CallbackQuery) -> None:
    material_id = int(call.data.split('.')[-1])
    material = get_material_by_id(material_id)
    
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_material_menu(material)
    )


def _handle_fill_field(bot: TeleBot, call: CallbackQuery) -> None:
    field = call.data.split('.')[-1]
    user_id = call.from_user.id
    
    if user_id not in admin_contexts:
        admin_contexts[user_id] = AdminContext()
    
    ctx = admin_contexts[user_id]
    ctx.menu_message_id = call.message.message_id
    
    prompts = {
        'title': (AdminState.FILLING_TITLE, "📝 Введите название материала:"),
        'message_text': (AdminState.FILLING_MESSAGE_TEXT, "💬 Введите текст сообщения:"),
        'photo': (AdminState.FILLING_PHOTO, "🖼 Отправьте фото:"),
        'document': (AdminState.FILLING_DOCUMENT, "📎 Отправьте файл:")
    }
    
    state, prompt = prompts[field]
    ctx.state = state
    
    msg = bot.send_message(
        chat_id=call.message.chat.id,
        message_thread_id=call.message.message_thread_id,
        text=prompt
    )
    ctx.request_message_id = msg.message_id


def _handle_edit_field(bot: TeleBot, call: CallbackQuery) -> None:
    field = call.data.split('.')[-1]
    user_id = call.from_user.id
    
    if user_id not in admin_contexts:
        bot.answer_callback_query(call.id, "❌ Контекст не найден", show_alert=True)
        return
    
    ctx = admin_contexts[user_id]
    ctx.menu_message_id = call.message.message_id
    
    prompts = {
        'title': (AdminState.FILLING_TITLE, "📝 Введите новое название материала:"),
        'message_text': (AdminState.FILLING_MESSAGE_TEXT, "💬 Введите новый текст сообщения:"),
        'photo': (AdminState.FILLING_PHOTO, "🖼 Отправьте новое фото:"),
        'document': (AdminState.FILLING_DOCUMENT, "📎 Отправьте новый файл:")
    }
    
    state, prompt = prompts[field]
    ctx.state = state
    
    msg = bot.send_message(
        chat_id=call.message.chat.id,
        message_thread_id=call.message.message_thread_id,
        text=prompt
    )
    ctx.request_message_id = msg.message_id


def _start_edit_material(bot: TeleBot, call: CallbackQuery) -> None:
    material_id = int(call.data.split('.')[-1])
    material = get_material_by_id(material_id)
    
    if not material:
        bot.answer_callback_query(call.id, "❌ Материал не найден", show_alert=True)
        return
    
    user_id = call.from_user.id
    admin_contexts[user_id] = AdminContext(
        category=material.category,
        material_id=material_id,
        title=material.title,
        message_text=material.message_text,
        media_file_id=material.media_file_id,
        document_file_ids=material.document_file_ids.copy() if material.document_file_ids else []
    )
    
    ctx = admin_contexts[user_id]
    
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_edit_material_menu(ctx)
        )


def _publish_material(bot: TeleBot, call: CallbackQuery) -> None:
    user_id = call.from_user.id
    ctx = admin_contexts.get(user_id)
    
    if not ctx or not ctx.title or not ctx.message_text:
        bot.answer_callback_query(call.id, "❌ Заполните обязательные поля", show_alert=True)
        return
    
    create_material(
        title=ctx.title,
        message_text=ctx.message_text,
        category=ctx.category,
        media_file_id=ctx.media_file_id,
        document_file_ids=ctx.document_file_ids
    )
    
    bot.answer_callback_query(call.id, "✅ Материал опубликован")
    del admin_contexts[user_id]
    
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_category_menu(ctx.category)
        )


def _save_material(bot: TeleBot, call: CallbackQuery) -> None:
    user_id = call.from_user.id
    ctx = admin_contexts.get(user_id)
    
    if not ctx or not ctx.material_id:
        bot.answer_callback_query(call.id, "❌ Контекст не найден", show_alert=True)
        return
    
    update_material(
        material_id=ctx.material_id,
        title=ctx.title,
        message_text=ctx.message_text,
        media_file_id=ctx.media_file_id,
        document_file_ids=ctx.document_file_ids
    )
    
    bot.answer_callback_query(call.id, "✅ Изменения сохранены")
    del admin_contexts[user_id]
    
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_category_menu(ctx.category)
        )


def _confirm_delete(bot: TeleBot, call: CallbackQuery) -> None:
    material_id = int(call.data.split('.')[-1])
    material = get_material_by_id(material_id)
    
    if not material:
        bot.answer_callback_query(call.id, "❌ Материал не найден", show_alert=True)
        return
    
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_delete_confirm(material_id)
        )


def _delete_file_from_material(bot: TeleBot, call: CallbackQuery) -> None:
    file_id = int(call.data.split('.')[-1])
    user_id = call.from_user.id
    
    ctx = admin_contexts.get(user_id)
    if not ctx:
        bot.answer_callback_query(call.id, "❌ Контекст не найден", show_alert=True)
        return
    
    if file_id in ctx.document_file_ids:
        ctx.document_file_ids.remove(file_id)
    
    delete_file(file_id)
    
    bot.answer_callback_query(call.id, "🗑 Файл удален")
    
    if ctx.material_id:
        menu_data = AdminMessages.get_edit_material_menu(ctx)
    else:
        menu_data = AdminMessages.get_create_material_menu(ctx)
    
    bot.edit_message_text(
        message_id=call.message.message_id,
        **menu_data
        )


def _delete_material(bot: TeleBot, call: CallbackQuery) -> None:
    material_id = int(call.data.split('.')[-1])
    material = get_material_by_id(material_id)
    
    if not material:
        bot.answer_callback_query(call.id, "❌ Материал не найден", show_alert=True)
        return
    
    category = material.category
    delete_material(material_id)
    
    bot.answer_callback_query(call.id, "✅ Материал удален")
    
    bot.edit_message_text(
        message_id=call.message.message_id,
        **AdminMessages.get_category_menu(category))


def _send_material_statistics(bot: TeleBot, call: CallbackQuery) -> None:
    material_id = int(call.data.split('.')[-1])
    material = get_material_by_id(material_id)
    
    if not material:
        bot.answer_callback_query(call.id, "❌ Материал не найден", show_alert=True)
        return
    
    statistics = get_material_statistics(material_id)
    
    if not statistics:
        bot.answer_callback_query(call.id, "📊 Пока нет просмотров", show_alert=True)
        return
    
    now = datetime.now()
    current_month_views = sum(
        1 for stat in statistics 
        if stat['viewed_at'] and stat['viewed_at'].year == now.year and stat['viewed_at'].month == now.month
    )
    
    filepath = create_statistics_excel(material_id, material.title, statistics)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    bot.send_document(
        chat_id=call.message.chat.id,
        message_thread_id=call.message.message_thread_id,
        document=InputFile(filepath),
        caption=f"📊 Статистика по материалу: {material.title}\n\nВсего просмотров: {len(statistics)}\nПросмотров в этом месяце: {current_month_views}",
    )
    bot.send_message(
        message_thread_id=call.message.message_thread_id,
        **AdminMessages.get_material_menu(material)
        )
    
    filepath.unlink()
    
    bot.answer_callback_query(call.id, "✅ Статистика отправлена")


def _export_users(bot: TeleBot, call: CallbackQuery) -> None:
    users = get_all_users_with_materials()
    
    if not users:
        bot.answer_callback_query(call.id, "📊 Пока нет пользователей", show_alert=True)
        return
    
    filepath = create_users_excel(users)
    
    completed_count = sum(1 for user in users if user['full_name'] and user['company'] and user['position'] and user['phone_number'])
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    bot.send_document(
        chat_id=call.message.chat.id,
        message_thread_id=call.message.message_thread_id,
        document=InputFile(filepath),
        caption=f"👥 Экспорт пользователей\n\nВсего пользователей: {len(users)}\nС заполненными контактами: {completed_count}",
    )
    bot.send_message(
        message_thread_id=call.message.message_thread_id,
        **AdminMessages.get_main_menu()
        )
    
    filepath.unlink()
    
    bot.answer_callback_query(call.id, "✅ Список пользователей отправлен")

