from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


def create_statistics_excel(material_id: int, material_title: str, statistics: list[dict]) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Статистика"
    
    headers = [
        "User ID",
        "Username",
        "Имя",
        "ФИО",
        "Компания",
        "Должность",
        "Телефон",
        "Дата и время"
    ]
    
    ws.append(headers)
    
    for stat in statistics:
        ws.append([
            stat['user_id'],
            stat['username'] or '',
            stat['first_name'] or '',
            stat['full_name'] or '',
            stat['company'] or '',
            stat['position'] or '',
            stat['phone_number'] or '',
            stat['viewed_at'].strftime('%d.%m.%Y %H:%M:%S') if stat['viewed_at'] else ''
        ])
    
    # Автоподгонка ширины колонок
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        
        adjusted_width = min(max_length + 2, 50)  # Максимум 50 символов
        ws.column_dimensions[column_letter].width = adjusted_width
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_title = "".join(c for c in material_title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:30]
    filename = f"stats_{material_id}_{safe_title}_{timestamp}.xlsx"
    filepath = Path(filename)
    
    wb.save(filepath)
    
    return filepath

