from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.config import moscow_now
from app.db.database import with_session
from app.db.models import Mailing, User


@with_session
def create_mailing(session: Session, message_type: str, message_text: str | None = None, media_file_id: str | None = None) -> Mailing:
    mailing = Mailing(
        message_type=message_type,
        message_text=message_text,
        media_file_id=media_file_id,
        status="draft"
    )
    session.add(mailing)
    session.flush()
    session.refresh(mailing)
    return mailing


@with_session
def get_mailing_by_id(session: Session, mailing_id: int) -> Mailing | None:
    stmt = select(Mailing).where(Mailing.id == mailing_id)
    return session.execute(stmt).scalar_one_or_none()


@with_session
def update_mailing_schedule(session: Session, mailing_id: int, scheduled_at: datetime) -> None:
    stmt = update(Mailing).where(Mailing.id == mailing_id).values(
        scheduled_at=scheduled_at,
        status="scheduled"
    )
    session.execute(stmt)


@with_session
def update_mailing_status(session: Session, mailing_id: int, status: str) -> None:
    values = {"status": status}
    if status == "completed":
        values["completed_at"] = moscow_now()
    
    stmt = update(Mailing).where(Mailing.id == mailing_id).values(**values)
    session.execute(stmt)


@with_session
def update_mailing_stats(session: Session, mailing_id: int, sent_count: int, blocked_count: int, error_count: int) -> None:
    stmt = update(Mailing).where(Mailing.id == mailing_id).values(
        sent_count=sent_count,
        blocked_count=blocked_count,
        error_count=error_count
    )
    session.execute(stmt)


@with_session
def get_active_users(session: Session) -> list[User]:
    stmt = select(User).where(User.is_blocked == False)
    return list(session.execute(stmt).scalars().all())


@with_session
def block_user(session: Session, user_id: int) -> None:
    stmt = update(User).where(User.user_id == user_id).values(is_blocked=True)
    session.execute(stmt)


@with_session
def get_scheduled_mailings(session: Session) -> list[Mailing]:
    stmt = select(Mailing).where(
        Mailing.status == "scheduled",
        Mailing.scheduled_at.isnot(None),
        Mailing.scheduled_at <= moscow_now()
    ).order_by(Mailing.scheduled_at)
    return list(session.execute(stmt).scalars().all())

