from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.bot.services.material_service import get_materials_by_category


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