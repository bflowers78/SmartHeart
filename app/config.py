import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")
DATABASE_URL: str = "sqlite:///./smartheart.db"

ADMIN_GROUP_ID: int = int(os.getenv("ADMIN_GROUP_ID"))
MAIN_TOPIC_ID: int = int(os.getenv("MAIN_TOPIC_ID"))
MAILING_TOPIC_ID: int = int(os.getenv("MAILING_TOPIC_ID"))
EVENTS_TOPIC_ID: int = int(os.getenv("EVENTS_TOPIC_ID"))

