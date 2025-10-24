from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import func
from telebot.types import User as TelegramUser
from app.db.models import User, UserMaterialView, Material
from app.db.database import with_session


@with_session
def create_user(session: Session, telegram_user: TelegramUser) -> bool:
    user = session.query(User).filter(User.user_id == telegram_user.id).first()
    
    if not user:
        user = User(
            user_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name
        )
        session.add(user)
        logger.info(f"Добавлен новый пользователь {telegram_user.id}:@{telegram_user.username}:{telegram_user.first_name}")
        return True
    
    return False


@with_session
def get_user_by_user_id(session: Session, user_id: int) -> User | None:
    return session.query(User).filter(User.user_id == user_id).first()


@with_session
def update_user_profile(session: Session, user_id: int, field: str, value: str) -> None:
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


@with_session
def update_user_consent(session: Session, user_id: int, consent_given: bool) -> None:
    user = session.query(User).filter(User.user_id == user_id).first()
    if user:
        user.is_consent_given = consent_given


@with_session
def update_user_lead_id(session: Session, user_id: int, lead_id: int) -> None:
    user = session.query(User).filter(User.user_id == user_id).first()
    if user:
        user.lead_id = lead_id


@with_session
def get_all_users_with_materials(session: Session) -> list[dict]:
    users = session.query(User).order_by(
        User.is_profile_completed.desc(),
        User.created_at.asc()
    ).all()
    
    result = []
    for user in users:
        materials = session.query(Material).join(
            UserMaterialView,
            Material.id == UserMaterialView.material_id
        ).filter(
            UserMaterialView.user_id == user.user_id
        ).all()
        
        result.append({
            'user_id': user.user_id,
            'username': user.username,
            'first_name': user.first_name,
            'full_name': user.full_name,
            'company': user.company,
            'position': user.position,
            'phone_number': user.phone_number,
            'created_at': user.created_at,
            'materials': [material.title for material in materials]
        })
    
    return result
