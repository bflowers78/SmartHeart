from sqlalchemy.orm import Session
from telebot.types import User as TelegramUser
from app.db.models import User
from app.db.database import with_session


@with_session
def create_user(session: Session, telegram_user: TelegramUser) -> None:
    user = session.query(User).filter(User.user_id == telegram_user.id).first()
    
    if not user:
        user = User(
            user_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name
        )
        session.add(user)


@with_session
def get_user_by_user_id(session: Session, user_id: int) -> User | None:
    return session.query(User).filter(User.user_id == user_id).first()


@with_session
def update_user_profile(session: Session, user_id: int, field: str, value: str) -> bool:
    user = session.query(User).filter(User.user_id == user_id).first()
    if user:
        if field == 'full_name':
            user.full_name = value
        elif field == 'company':
            user.company = value
        elif field == 'position':
            user.position = value
        elif field == 'phone_number':
            user.phone_number = value
        
        if user.full_name and user.company and user.position and user.phone_number:
            user.is_profile_completed = True
        
        return True
    return False
