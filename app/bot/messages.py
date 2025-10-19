from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.bot.admin_handlers.states import AdminContext
from app.bot.services.material_service import get_materials_by_category
from app.bot.services.file_service import get_files_by_ids


class Messages:
    @staticmethod
    def get_main_menu() -> dict:
        return {
        'text': '🏠 *Главное меню пользователя*',
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
        markup.add(InlineKeyboardButton('Стать участником', callback_data='main_menu'))
        markup.add(InlineKeyboardButton('Стать зрителем', callback_data='main_menu'))
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
            InlineKeyboardButton('Smart Heart a тепетрами', callback_data='smart_heart_tepetrami'),
            InlineKeyboardButton('Портфолио', callback_data='portfolio'),
            InlineKeyboardButton('Команда', callback_data='team'),
            InlineKeyboardButton('Оставить замоку', callback_data='leave_request'),
            InlineKeyboardButton('Услуги', callback_data='services'),
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
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton('👥 Пользователи', callback_data='admin.users'),
            InlineKeyboardButton('💡 Продукты', callback_data='admin.category.product'),
            InlineKeyboardButton('📕 Полезные материалы', callback_data='admin.category.helpful'),
            InlineKeyboardButton('🔥 Прожарка', callback_data='admin.category.roasting')
        )
        return {
            'text': '🏠 *Админ меню*\n\nВыберите раздел:',
            'parse_mode': 'Markdown',
            'reply_markup': markup
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
            'text': '✏️ *Редактирование материала*\n\nИзмените данные:',
            'parse_mode': 'Markdown',
            'reply_markup': markup
        }
    
    @staticmethod
    def get_material_menu(material_id: int, category: str) -> dict:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton('📊 Статистика', callback_data='admin.stats'),
            InlineKeyboardButton('✏️ Редактировать', callback_data=f'admin.edit_start.{material_id}'),
            InlineKeyboardButton('🗑 Удалить материал', callback_data=f'admin.delete_confirm.{material_id}'),
            InlineKeyboardButton('🔙 Назад', callback_data=f'admin.category.{category}')
        )
        
        return {
            'reply_markup': markup
        }
    
    @staticmethod
    def get_delete_confirm(material_id: int, category: str) -> dict:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton('✅ Да, удалить', callback_data=f'admin.delete.{material_id}'),
            InlineKeyboardButton('❌ Отмена', callback_data=f'admin.material.{material_id}')
        )
        
        return {
            'text': '⚠️ *Подтверждение удаления*\n\nВы уверены, что хотите удалить этот материал?',
            'parse_mode': 'Markdown',
            'reply_markup': markup
        }