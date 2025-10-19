from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, User as TelegramUser
from app.bot.admin_handlers.states import AdminContext
from app.bot.services.material_service import get_materials_by_category
from app.bot.services.file_service import get_files_by_ids
from app.config import ADMIN_GROUP_ID, EVENTS_TOPIC_ID, MAIN_TOPIC_ID
from app.db.models import User, Material


class Messages:
    @staticmethod
    def get_main_menu() -> dict:
        return {
        'text': 'Привет! Команда *SmartHeart* разработала бота, кторый поможет найти всю необходимую информацию. '
                'Мы попросим васподелться контатами, но обещаем, что хотим только познакомиться, а не устраивать спам-атаки)\n\n'
                'Сейчас ты в *Главном меню*. Выбирай, куда отправишься дальше.',
        'parse_mode': 'Markdown',
        'reply_markup': InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton('💡 Продукты', callback_data='products'),
            InlineKeyboardButton('📕 Полезные материалы', callback_data='materials'),
            InlineKeyboardButton('🔥 Прожарка', callback_data='roasting'),
            InlineKeyboardButton('ℹ️ О нас', callback_data='about')
        )
    }


    @staticmethod
    def get_profile_fill_menu(user) -> dict:
        full_name_status = user.full_name if user.full_name else "Не заполнено"
        company_status = user.company if user.company else "Не заполнено"
        position_status = user.position if user.position else "Не заполнено"
        phone_status = user.phone_number if user.phone_number else "Не заполнено"
        
        return {
            'text': '📝 *Заполните все поля для доступа к материалам*',
            'parse_mode': 'Markdown',
            'reply_markup': InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(f'ФИО: {full_name_status}', callback_data='fill.full_name'),
                InlineKeyboardButton(f'Компания: {company_status}', callback_data='fill.company'),
                InlineKeyboardButton(f'Должность: {position_status}', callback_data='fill.position'),
                InlineKeyboardButton(f'Номер телефона: {phone_status}', callback_data='fill.phone'),
                InlineKeyboardButton('💾 Сохранить', callback_data='save_data'),
                InlineKeyboardButton('🏠 Главное меню', callback_data='main_menu')
            )
        }

    @staticmethod
    def get_products_menu() -> dict:
        materials = get_materials_by_category('product')
        markup = InlineKeyboardMarkup(row_width=1)
        for material in materials:
            markup.add(InlineKeyboardButton(material.title, callback_data=f'get_material.{material.id}'))
        markup.add(InlineKeyboardButton('🏠 Главное меню', callback_data='main_menu'))
        
        return {
            'text': '💡 *Продукты*',
            'parse_mode': 'Markdown',
            'reply_markup': markup
        }

    @staticmethod
    def get_materials_menu() -> dict:
        materials = get_materials_by_category('helpful')
        markup = InlineKeyboardMarkup(row_width=1)
        for material in materials:
            markup.add(InlineKeyboardButton(material.title, callback_data=f'get_material.{material.id}'))
        markup.add(InlineKeyboardButton('🏠 Главное меню', callback_data='main_menu'))
        
        return {
            'text': '📕 *Полезные материалы*',
            'parse_mode': 'Markdown',
            'reply_markup': markup
        }

    @staticmethod
    def get_roasting_menu() -> dict:
        materials = get_materials_by_category('roasting')
        markup = InlineKeyboardMarkup(row_width=1)
        for material in materials:
            markup.add(InlineKeyboardButton(material.title, callback_data=f'get_material.{material.id}'))
        markup.add(InlineKeyboardButton('Стать участником', callback_data='become_participant'))
        markup.add(InlineKeyboardButton('Стать зрителем', callback_data='become_viewer'))
        markup.add(InlineKeyboardButton('🏠 Главное меню', callback_data='main_menu'))
        
        return {
            'text': '🔥 *Прожарка*',
            'parse_mode': 'Markdown',
            'reply_markup': markup
        }

    @staticmethod
    def get_about_menu() -> dict:
        return {
        'text': '🏠 *О нас*',
        'parse_mode': 'Markdown',
        'reply_markup': InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton('SmartHeart в телеграмм', url='https://lcvr.net/s/PSRGV'),
            InlineKeyboardButton('Портфолио', url='https://lcvr.net/s/gzxsY'),
            InlineKeyboardButton('Команда', url='https://lcvr.net/s/GG8PB'),
            InlineKeyboardButton('Оставить замоку', url='https://lcvr.net/s/JdcdH'),
            InlineKeyboardButton('Услуги', url='https://lcvr.net/s/sxdGt'),
            InlineKeyboardButton('🏠 Главное меню', callback_data='main_menu')
        )
    }

class AdminMessages:
    CATEGORY_NAMES = {
        'product': '💡 Продукты',
        'helpful': '📕 Полезные материалы',
        'roasting': '🔥 Прожарка'
    }
    
    @staticmethod
    def get_main_menu() -> dict:
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': '🏠 *Админ меню*\n\nВыберите раздел:',
            'parse_mode': 'Markdown',
            'reply_markup': InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton('👥 Пользователи', callback_data='admin.users'),
                InlineKeyboardButton('💡 Продукты', callback_data='admin.category.product'),
                InlineKeyboardButton('📕 Полезные материалы', callback_data='admin.category.helpful'),
                InlineKeyboardButton('🔥 Прожарка', callback_data='admin.category.roasting')
            )
        }
    
    @staticmethod
    def get_category_menu(category: str) -> dict:
        materials = get_materials_by_category(category)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton('➕ Добавить материал', callback_data=f'admin.add.{category}'))
        
        for material in materials:
            markup.add(InlineKeyboardButton(material.title, callback_data=f'admin.material.{material.id}'))
        
        markup.add(InlineKeyboardButton('🏠 Главное меню', callback_data='admin.main'))
        
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': f'{AdminMessages.CATEGORY_NAMES[category]}\n\nВыберите действие:',
            'parse_mode': 'Markdown',
            'reply_markup': markup
        }
    
    @staticmethod
    def get_create_material_menu(ctx: AdminContext) -> dict:
        title_status = ctx.title if ctx.title else "Не заполнено"
        text_status = "Заполнено" if ctx.message_text else "Не заполнено"
        photo_status = "Добавлено" if ctx.media_file_id else "Не добавлено"
        
        markup = InlineKeyboardMarkup(row_width=1)
        
        can_publish = ctx.title and ctx.message_text
        publish_btn = InlineKeyboardButton(
            '✅ Опубликовать' if can_publish else 'Опубликовать',
            callback_data='admin.publish' if can_publish else 'admin.noop'
        )
        markup.add(publish_btn)
        
        markup.add(
            InlineKeyboardButton(f'📝 Название: {title_status}', callback_data='admin.fill.title'),
            InlineKeyboardButton(f'💬 Текст: {text_status}', callback_data='admin.fill.message_text'),
            InlineKeyboardButton(f'🖼 Фото: {photo_status}', callback_data='admin.fill.photo')
        )
        
        if ctx.document_file_ids:
            files = get_files_by_ids(ctx.document_file_ids)
            for file in files:
                markup.add(InlineKeyboardButton(f'📎 {file.file_name}', callback_data=f'admin.delete_file.{file.id}'))
        
        markup.add(
            InlineKeyboardButton('➕ Добавить файл', callback_data='admin.fill.document'),
            InlineKeyboardButton('🔙 Назад', callback_data=f'admin.category.{ctx.category}')
        )
        
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': '📝 *Создание материала*\n\nЗаполните данные:',
            'parse_mode': 'Markdown',
            'reply_markup': markup
        }
    
    @staticmethod
    def get_edit_material_menu(ctx: AdminContext) -> dict:
        title_status = ctx.title if ctx.title else "Не заполнено"
        text_status = "Заполнено" if ctx.message_text else "Не заполнено"
        photo_status = "Добавлено" if ctx.media_file_id else "Не добавлено"
        
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(f'📝 Название: {title_status}', callback_data='admin.edit.title'),
            InlineKeyboardButton(f'💬 Текст: {text_status}', callback_data='admin.edit.message_text'),
            InlineKeyboardButton(f'🖼 Фото: {photo_status}', callback_data='admin.edit.photo')
        )
        
        if ctx.document_file_ids:
            files = get_files_by_ids(ctx.document_file_ids)
            for file in files:
                markup.add(InlineKeyboardButton(f'📎 {file.file_name}', callback_data=f'admin.delete_file.{file.id}'))
        
        markup.add(
            InlineKeyboardButton('➕ Добавить файл', callback_data='admin.edit.document'),
            InlineKeyboardButton('💾 Сохранить', callback_data='admin.save'),
            InlineKeyboardButton('🔙 Назад', callback_data=f'admin.material.{ctx.material_id}')
        )
        
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': '✏️ *Редактирование материала*\n\nИзмените данные:',
            'parse_mode': 'Markdown',
            'reply_markup': markup
        }
    
    @staticmethod
    def get_material_menu(material: Material) -> dict:
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': material.message_text,
            'parse_mode': 'Markdown',
            'reply_markup': InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton('📊 Статистика', callback_data=f'admin.stats.{material.id}'),
                InlineKeyboardButton('✏️ Редактировать', callback_data=f'admin.edit_start.{material.id}'),
                InlineKeyboardButton('🗑 Удалить материал', callback_data=f'admin.delete_confirm.{material.id}'),
                InlineKeyboardButton('🔙 Назад', callback_data=f'admin.category.{material.category}')
            )
        }
    
    @staticmethod
    def get_delete_confirm(material_id: int) -> dict:
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': '⚠️ *Подтверждение удаления*\n\nВы уверены, что хотите удалить этот материал?',
            'parse_mode': 'Markdown',
            'reply_markup': InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton('✅ Да, удалить', callback_data=f'admin.delete.{material_id}'),
                InlineKeyboardButton('❌ Отмена', callback_data=f'admin.material.{material_id}')
            )
        }
    
    @staticmethod
    def new_user(telegram_user: TelegramUser) -> dict:
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': (
                f"🆕 <b>Новый пользователь</b>\n\n"
                f"👤 ID: <code>{telegram_user.id}</code>\n"
                f"📛 Имя: {telegram_user.first_name or 'Не указано'}\n"
                f"🔗 Username: @{telegram_user.username or 'Не указано'}"
            ),
            'message_thread_id': EVENTS_TOPIC_ID,
            'parse_mode': 'HTML'
        }
    
    @staticmethod
    def profile_completed(user: User) -> dict:
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': (
                f"📞 <b>Пользователь поделился контактами</b>\n\n"
                f"👤 ID: <code>{user.user_id}</code>\n"
                f"📛 ФИО: {user.full_name}\n"
                f"🏢 Компания: {user.company}\n"
                f"💼 Должность: {user.position}\n"
                f"📞 Телефон: {user.phone_number}\n"
                f"🔗 Username: @{user.username or 'Не указано'}"
            ),
            'message_thread_id': EVENTS_TOPIC_ID,
            'parse_mode': 'HTML'
        }
    
    @classmethod
    def material_interest(cls, user_id: int, username: str | None, material: Material) -> dict:
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': (
                f"📚 <b>Интерес к материалу</b>\n\n"
                f"👤 ID: <code>{user_id}</code>\n"
                f"🔗 Username: @{username or 'Не указано'}\n"
                f"📄 Материал: <b>{material.title}</b>\n"
                f"🏷 Категория: <b>{cls.CATEGORY_NAMES[material.category]}</b>"
            ),
            'message_thread_id': EVENTS_TOPIC_ID,
            'parse_mode': 'HTML'
        }
    
    @staticmethod
    def roasting_request(user: User, request_type: str) -> dict:
        request_label = "участником" if request_type == "participant" else "зрителем"
        return {
            'chat_id': ADMIN_GROUP_ID,
            'text': (
                f"🔥 <b>Заявка на участие в прожарке</b>\n\n"
                f"👤 ID: <code>{user.user_id}</code>\n"
                f"📛 ФИО: {user.full_name or 'Не указано'}\n"
                f"🏢 Компания: {user.company or 'Не указано'}\n"
                f"💼 Должность: {user.position or 'Не указано'}\n"
                f"📞 Телефон: {user.phone_number or 'Не указано'}\n"
                f"🔗 Username: @{user.username or 'Не указано'}\n\n"
                f"Хочет стать <b>{request_label}</b>"
            ),
            'message_thread_id': EVENTS_TOPIC_ID,
            'parse_mode': 'HTML'
        }