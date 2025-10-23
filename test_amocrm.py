from app.bot.services.amocrm_service import create_lead, get_leads, get_lead, add_note_to_lead

# print("=== Получение списка сделок ===")
# leads = get_leads(limit=10)
# if leads:
#     print(f"Получено сделок: {len(leads)}")
#     for lead in leads[:3]:
#         print(f"  - ID: {lead['id']}, Название: {lead['name']}, Бюджет: {lead.get('price', 0)}")
# else:
#     print("Не удалось получить список сделок")

# print("\n=== Получение конкретной сделки ===")
# lead_id = 1045091
# lead_detail = get_lead(lead_id)
# if lead_detail:
    
#     print(f"Сделка ID {lead_id}:")
#     print(f"  Название: {lead_detail['name']}")
#     print(f"  Бюджет: {lead_detail.get('price', 0)}")
#     print(f"  Статус ID: {lead_detail.get('status_id')}")
#     print(lead_detail)

# print("\n=== Создание новой сделки с примечанием ===")
# new_lead_id = create_lead(name="Заявка на консультацию. Тест")
# if new_lead_id:
#     print(f"Создана сделка с ID: {new_lead_id}")
    
#     # Формируем текст примечания с контактами и материалом
#     contact_info = "Телефон: +7 999 123-45-67\nEmail: user@example.com\nTelegram: @username"
#     material_info = "Интересующий материал: Курс по Python для начинающих"
    
#     note_text = f"{contact_info}\n\n{material_info}"
    
#     # Добавляем примечание
#     if add_note_to_lead(new_lead_id, note_text):
#         print("Примечание успешно добавлено")
#     else:
#         print("Не удалось добавить примечание")
# else:
#     print("Не удалось создать сделку")

