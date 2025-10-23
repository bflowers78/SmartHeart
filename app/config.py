import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
DATABASE_URL: str = "sqlite:///./smartheart.db"

ADMIN_GROUP_ID: int = int(os.getenv("ADMIN_GROUP_ID"))
MAIN_TOPIC_ID: int = int(os.getenv("MAIN_TOPIC_ID"))
MAILING_TOPIC_ID: int = int(os.getenv("MAILING_TOPIC_ID"))
EVENTS_TOPIC_ID: int = int(os.getenv("EVENTS_TOPIC_ID"))

AMOCRM_URL: str = os.getenv("AMOCRM_URL")
AMOCRM_ACCESS_TOKEN: str = os.getenv("AMOCRM_ACCESS_TOKEN")
AMOCRM_PIPELINE_ID: int = int(os.getenv("AMOCRM_PIPELINE_ID", "0"))

MOSCOW_TZ = timezone(timedelta(hours=3))


def moscow_now() -> datetime:
    return datetime.now(MOSCOW_TZ)

