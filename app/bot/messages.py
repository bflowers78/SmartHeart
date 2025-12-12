from datetime import datetime
from typing import TYPE_CHECKING
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, User as TelegramUser
from app.bot.services.material_service import get_materials_by_category
from app.bot.services.file_service import get_files_by_ids
from app.config import ADMIN_GROUP_ID, EVENTS_TOPIC_ID
from app.db.models import User, Material, Mailing

if TYPE_CHECKING:
    from app.bot.admin_handlers.states import AdminContext, MailingContext
    

class Messages:
    @staticmethod
    def get_main_menu() -> dict:
        return {
        'text': 'Привет! Команда креативного агентства Умное Сердце (ex. SmartHeart) разработала бота, '
                'чтобы делиться полезными материалами, мероприятиями и новостями из мира брендинга и креатива.😇 \n\n'
                'Мы попросим тебя поделиться контактами, но обещаем, что хотим только познакомиться, а не устраивать спам-атаки)\n\n'
                'Сейчас ты в главном меню. Выбирай, куда отправишься дальше.',
        'parse_mode': 'Markdown',
        'reply_markup': InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton('💡 Продукты', callback_data='products'),
            InlineKeyboardButton('📕 Полезные материалы', callback_data='materials'),
            InlineKeyboardButton('🔥 Прожарка', callback_data='roasting'),
            InlineKeyboardButton('ℹ️ О нас', callback_data='about')
        )
    }


    @staticmethod
    def get_consent_message() -> dict:
        return {
            'text': ('Чтобы продолжить работу с ботом и получить доступ к материалам, пожалуйста, ознакомьтесь с документами и подтвердите своё согласие.\n\n'
                    '*Нажимая кнопку «Принять», вы:*\n\n'
                    '— Подтверждаете, что ознакомились с указанными документами;\n'
                    '— Даёте добровольное и информированное [согласие на обработку персональных данных](https://sh.agency/upload/files/soglasiye.pdf) в соответствии с Федеральным законом № 152-ФЗ «О персональных данных»;\n'
                    '— Принимаете условия [Политики конфиденциальности](https://sh.agency/upload/files/politika.pdf).\n\n'
                    '_Если вы не согласны с условиями, использование бота можно прекратить в любой момент._'),
            'parse_mode': 'Markdown',
            'reply_markup': InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton('✅ Принять', callback_data='accept_consent')
            ),
            'disable_web_page_preview': True
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
            'text': '*👋 Добро пожаловать в раздел «Продукты».*\n\n'
                    'Здесь — всё, что делает Умное Сердце особенным.\n\n'
                    'Мы создаём стратегии, айдентики, нейминги, креативные концепции, рекламные кампании и сервис-дизайн. '
                    'Помогаем брендам понимать себя, говорить честно и звучать громко.\n\n'
                    'Каждый бренд (как и человек) хочет быть значимым, нужным, настоящим.\n'
                    'Мы просто помогаем это проявить 💡',
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
            'text': '*Хотите прокачать свой бренд без лишних проб и ошибок?*\n\n'
                    'У нас есть для вас лайфхаки, чек-листы и гайды, которые:\n\n'
                    '▫️Сэкономят часы вашего времени - берите готовые решения, а не изобретайте велосипед,\n'
                    '▫️Уберегут от факапов - учитесь на чужих ошибках, а не на своих,\n'
                    '▫️Раскроют скрытые возможности - используйте брендинг на полную!\n\n'
                    'Ловите подборку экспертизы от\n'
                    'Умное Сердце - и ваш бренд скажет вам «спасибо»!\n',
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
            'text': '*👋 Привет! Это прожарка брендов!*\n\n'
                    'В Умное Сердце мы верим, что брендинг — это точная работа, и нам важно не только создавать сильные бренды, но и показывать, как брендинг работает на практике.\n\n'
                    '*Что такое «Прожарка»?*\n Это открытый разбор брендов, где мы оцениваем их по трём уровням:\n\n'
                    'Смысл — как бренд резонирует с аудиторией.\n'
                    'Визуал — отражает ли дизайн идеи бренда.\n'
                    'Коммуникации — насколько эффективно доносится ценность бренда.\n\n'
                    '*В боте вы найдете:*\n\n'
                    '🔥 Чек-лист для самодиагностики бренда\n'
                    '🎥 Запись последней прожарки\n'
                    '📝 Регистрацию на следующую прожарку (зритель или участник)',
            'parse_mode': 'Markdown',
            'reply_markup': markup,
            'disable_web_page_preview': True
        }

    @staticmethod
    def get_about_menu() -> dict:
        return {
        'text': '🏠 *О нас*',
        'parse_mode': 'Markdown',
        'reply_markup': InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton('Умное Сердце в телеграмм', url='https://t.me/+gwVzMMDzODExNGEy'),
            InlineKeyboardButton('Портфолио', url='https://lcvr.net/s/gzxsY'),
            InlineKeyboardButton('Команда', url='https://lcvr.net/s/GG8PB'),
            InlineKeyboardButton('Оставить заявку', url='https://lcvr.net/s/JdcdH'),
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
    def get_create_material_menu(ctx: 'AdminContext') -> dict:
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
    def get_edit_material_menu(ctx: 'AdminContext') -> dict:
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
    
    @staticmethod
    def get_mailing_confirmation(mailing_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton('📅 Запланировать отправку', callback_data=f'mail.schedule.{mailing_id}'),
            InlineKeyboardButton('🚀 Отправить сейчас', callback_data=f'mail.send_now.{mailing_id}')
        )
    
    @staticmethod
    def get_calendar_menu(mailing_id: int, current_date: datetime | None = None) -> InlineKeyboardMarkup:
        if not current_date:
            current_date = datetime.now()
        
        markup = InlineKeyboardMarkup(row_width=7)
        
        year = current_date.year
        month = current_date.month
        
        markup.add(InlineKeyboardButton(f'📅 {current_date.strftime("%B %Y")}', callback_data='mail.noop'))
        
        days_row = [InlineKeyboardButton(day, callback_data='mail.noop') for day in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']]
        markup.row(*days_row)
        
        from calendar import monthcalendar
        cal = monthcalendar(year, month)
        
        for week in cal:
            week_buttons = []
            for day in week:
                if day == 0:
                    week_buttons.append(InlineKeyboardButton(' ', callback_data='mail.noop'))
                else:
                    date_obj = datetime(year, month, day)
                    if date_obj.date() < datetime.now().date():
                        week_buttons.append(InlineKeyboardButton(f'·{day}·', callback_data='mail.noop'))
                    else:
                        week_buttons.append(InlineKeyboardButton(f'{day}', callback_data=f'mail.date.{mailing_id}.{year}.{month}.{day}'))
            markup.row(*week_buttons)
        
        nav_buttons = []
        if month > 1:
            nav_buttons.append(InlineKeyboardButton('◀️', callback_data=f'mail.cal.{mailing_id}.{year}.{month-1}'))
        else:
            nav_buttons.append(InlineKeyboardButton('◀️', callback_data=f'mail.cal.{mailing_id}.{year-1}.12'))
        
        if month < 12:
            nav_buttons.append(InlineKeyboardButton('▶️', callback_data=f'mail.cal.{mailing_id}.{year}.{month+1}'))
        else:
            nav_buttons.append(InlineKeyboardButton('▶️', callback_data=f'mail.cal.{mailing_id}.{year+1}.1'))
        
        markup.row(*nav_buttons)
        markup.add(InlineKeyboardButton('❌ Отмена', callback_data=f'mail.cancel.{mailing_id}'))
        
        return markup
    
    @staticmethod
    def get_time_menu(mailing_id: int, ctx: 'MailingContext') -> InlineKeyboardMarkup:
        current_time = ctx.scheduled_time or datetime.now().replace(second=0, microsecond=0)
        
        time_str = current_time.strftime('%H:%M')
        date_str = ctx.scheduled_date.strftime('%d.%m') if ctx.scheduled_date else '??.??'
        
        markup = InlineKeyboardMarkup(row_width=4)
        markup.add(InlineKeyboardButton(f'🕐 {date_str} {time_str}', callback_data='mail.schedule.{mailing_id}'))
        markup.row(
            InlineKeyboardButton('-1ч', callback_data=f'mail.time.{mailing_id}.-60'),
            InlineKeyboardButton('-10м', callback_data=f'mail.time.{mailing_id}.-10'),
            InlineKeyboardButton('+10м', callback_data=f'mail.time.{mailing_id}.10'),
            InlineKeyboardButton('+1ч', callback_data=f'mail.time.{mailing_id}.60')
        )
        
        markup.add(InlineKeyboardButton('💾 Сохранить', callback_data=f'mail.save_schedule.{mailing_id}'))
        markup.add(InlineKeyboardButton('❌ Отмена', callback_data=f'mail.cancel.{mailing_id}'))
        
        return markup
    
    @staticmethod
    def get_scheduled_mailing_info(mailing: Mailing) -> InlineKeyboardMarkup:
        scheduled_str = mailing.scheduled_at.strftime('%d.%m %H:%M') if mailing.scheduled_at else '??.?? ??:??'
        
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(f'✅ Запланировано: {scheduled_str}', callback_data='mail.noop'),
            InlineKeyboardButton('📅 Дата', callback_data=f'mail.schedule.{mailing.id}'),
            InlineKeyboardButton('🕐 Время', callback_data=f'mail.edit_time.{mailing.id}')
        )
    
    @staticmethod
    def get_mailing_progress(mailing_id: int, total: int, sent: int, blocked: int, errors: int) -> InlineKeyboardMarkup:
        progress = int((sent + blocked + errors) / total * 100) if total > 0 else 0
        progress_bar = '█' * (progress // 10) + '░' * (10 - progress // 10)
        
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(f'📬 Рассылка #{mailing_id}', callback_data='mail.noop'),
            InlineKeyboardButton(f'{progress_bar} {progress}%', callback_data='mail.noop'),
            InlineKeyboardButton(f'✅ {sent}/{total} | 🚫 {blocked} | ❌ {errors}', callback_data='mail.noop'),
            InlineKeyboardButton('⏸ Приостановить', callback_data=f'mail.pause.{mailing_id}')
        )
    
    @staticmethod
    def get_mailing_completed(mailing: Mailing, total: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(f'✅ Рассылка #{mailing.id} завершена', callback_data='mail.noop'),
            InlineKeyboardButton(f'📊 Отправлено: {mailing.sent_count}/{total}', callback_data='mail.noop'),
            InlineKeyboardButton(f'🚫 Заблокировано: {mailing.blocked_count}', callback_data='mail.noop'),
            InlineKeyboardButton(f'❌ Ошибок: {mailing.error_count}', callback_data='mail.noop')
        )