from typing import Optional
import requests
from loguru import logger
from app.config import AMOCRM_URL, AMOCRM_ACCESS_TOKEN, AMOCRM_PIPELINE_ID

URL: str = f"{AMOCRM_URL}/api/v4/leads"
HEADERS: dict[str, str] = {
    "Authorization": f"Bearer {AMOCRM_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


def get_leads(limit: int = 50, page: int = 1) -> Optional[list[dict]]:
    """Получает список сделок из AMO CRM"""
    params = {"limit": limit, "page": page}
    
    try:
        response = requests.get(URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        leads = result.get("_embedded", {}).get("leads", [])
        
        logger.info(f"Получено {len(leads)} сделок из AMO CRM")
        return leads
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении списка сделок из AMO CRM: {e}")
        return None


def get_lead(lead_id: int) -> Optional[dict]:
    """Получает данные конкретной сделки из AMO CRM"""
    try:
        response = requests.get(f"{URL}/{lead_id}", headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Получена сделка ID {lead_id} из AMO CRM")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении сделки ID {lead_id} из AMO CRM: {e}")
        return None


def create_lead(name: str, user_id: Optional[int] = None, custom_fields: Optional[dict] = None) -> Optional[int]:
    """Создает сделку в AMO CRM"""
    
    lead_data = {
        "name": name,
        "pipeline_id": AMOCRM_PIPELINE_ID
    }
    
    if user_id:
        lead_data["responsible_user_id"] = user_id
    
    if custom_fields:
        lead_data["custom_fields_values"] = [
            {"field_id": field_id, "values": [{"value": value}]}
            for field_id, value in custom_fields.items()
        ]
    
    payload = [lead_data]
    
    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        lead_id = result["_embedded"]["leads"][0]["id"]
        
        logger.info(f"Создана сделка в AMO CRM: ID {lead_id}, название '{name}'")
        return lead_id
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при создании сделки в AMO CRM: {e}")
        return None


def add_note_to_lead(lead_id: int, text: str) -> bool:
    """Добавляет примечание к сделке в AMO CRM"""
    note_url = f"{URL}/{lead_id}/notes"
    
    payload = [
        {
            "note_type": "common",
            "params": {"text": text}
        }
    ]
    
    try:
        response = requests.post(note_url, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Добавлено примечание к сделке ID {lead_id}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при добавлении примечания к сделке ID {lead_id}: {e}")
        return False
