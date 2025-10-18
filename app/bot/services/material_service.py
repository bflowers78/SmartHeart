from sqlalchemy.orm import Session
from app.db.models import Material
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

