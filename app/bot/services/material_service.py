from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import Material, UserMaterialView, User
from app.db.database import with_session


@with_session
def get_material_by_id(session: Session, material_id: int) -> Material | None:
    return session.query(Material).filter(Material.id == material_id).first()


@with_session
def get_materials_by_category(session: Session, category: str) -> list[Material]:
    return session.query(Material).filter(Material.category == category).all()


@with_session
def create_material(session: Session, title: str, category: str, message_text: str, media_file_id: str | None = None, document_file_ids: list[str] | None = None) -> None:
    material = Material(
        title=title,
        message_text=message_text,
        media_file_id=media_file_id,
        document_file_ids=document_file_ids or [],
        category=category
    )
    session.add(material)


@with_session
def update_material(session: Session, material_id: int, title: str | None = None, message_text: str | None = None, media_file_id: str | None = None, document_file_ids: list[str] | None = None, category: str | None = None) -> bool:
    material = session.query(Material).filter(Material.id == material_id).first()
    if material:
        if title is not None:
            material.title = title
        if message_text is not None:
            material.message_text = message_text
        if media_file_id is not None:
            material.media_file_id = media_file_id
        if document_file_ids is not None:
            material.document_file_ids = document_file_ids
        if category is not None:
            material.category = category
        return True
    return False


@with_session
def delete_material(session: Session, material_id: int) -> bool:
    material = session.query(Material).filter(Material.id == material_id).first()
    if material:
        session.delete(material)
        return True
    return False


@with_session
def record_material_view(session: Session, user_id: int, material_id: int) -> None:
    view = UserMaterialView(user_id=user_id, material_id=material_id)
    session.add(view)


@with_session
def get_user_viewed_materials(session: Session, user_id: int) -> list[int]:
    views = session.query(UserMaterialView.material_id).filter(UserMaterialView.user_id == user_id).distinct().all()
    return [view[0] for view in views]


@with_session
def get_material_statistics(session: Session, material_id: int) -> list[dict]:
    from sqlalchemy import func
    
    subquery = (
        select(
            UserMaterialView.user_id,
            func.max(UserMaterialView.viewed_at).label('last_viewed')
        )
        .filter(UserMaterialView.material_id == material_id)
        .group_by(UserMaterialView.user_id)
        .subquery()
    )
    
    result = session.execute(
        select(
            User.user_id,
            User.username,
            User.first_name,
            User.full_name,
            User.company,
            User.position,
            User.phone_number,
            subquery.c.last_viewed
        )
        .join(subquery, User.user_id == subquery.c.user_id)
        .order_by(subquery.c.last_viewed.asc())
    ).all()
    
    return [
        {
            'user_id': row[0],
            'username': row[1],
            'first_name': row[2],
            'full_name': row[3],
            'company': row[4],
            'position': row[5],
            'phone_number': row[6],
            'viewed_at': row[7]
        }
        for row in result
    ]

