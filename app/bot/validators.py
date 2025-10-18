import re

def validate_full_name(full_name: str) -> tuple[bool, str]:
    """Валидация ФИО"""
    if not full_name or len(full_name.strip()) < 5:
        return False, "ФИО должно содержать минимум 5 символов"
    
    if len(full_name.strip()) > 255:
        return False, "ФИО слишком длинное (максимум 255 символов)"
    
    # Проверка на наличие только букв, пробелов и дефисов
    if not re.match(r'^[а-яёА-ЯЁa-zA-Z\s\-]+$', full_name.strip()):
        return False, "ФИО должно содержать только буквы, пробелы и дефисы"
    
    return True, ""


def validate_company(company: str) -> tuple[bool, str]:
    """Валидация названия компании"""
    if not company or len(company.strip()) < 2:
        return False, "Название компании должно содержать минимум 2 символа"
    
    if len(company.strip()) > 255:
        return False, "Название компании слишком длинное (максимум 255 символов)"
    
    return True, ""


def validate_position(position: str) -> tuple[bool, str]:
    """Валидация должности"""
    if not position or len(position.strip()) < 2:
        return False, "Должность должна содержать минимум 2 символа"
    
    if len(position.strip()) > 255:
        return False, "Должность слишком длинная (максимум 255 символов)"
    
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """Валидация номера телефона"""
    if not phone:
        return False, "Номер телефона не может быть пустым"
    
    # Убираем все символы кроме цифр
    clean_phone = re.sub(r'\D', '', phone)
    
    if len(clean_phone) < 10:
        return False, "Номер телефона должен содержать минимум 10 цифр"
    
    if len(clean_phone) > 15:
        return False, "Номер телефона слишком длинный (максимум 15 цифр)"
    
    # Проверяем что номер начинается с правильного кода
    if not re.match(r'^(\+?7|8)', clean_phone):
        return False, "Номер должен начинаться с +7, 7 или 8"
    
    return True, ""
