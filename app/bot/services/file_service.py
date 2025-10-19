from sqlalchemy.orm import Session
from app.db.models import File
from app.db.database import with_session


@with_session
def create_file(session: Session, file_name: str, file_extension: str, file_id: str) -> File:
    existing_file = session.query(File).filter(File.file_id == file_id).first()
    if existing_file:
        return existing_file
    
    file = File(
        file_name=file_name,
        file_extension=file_extension,
        file_id=file_id
    )
    session.add(file)
    session.flush()
    return file


@with_session
def get_file_by_id(session: Session, file_id: int) -> File | None:
    return session.query(File).filter(File.id == file_id).first()


@with_session
def get_files_by_ids(session: Session, file_ids: list[int]) -> list[File]:
    return session.query(File).filter(File.id.in_(file_ids)).all()


@with_session
def delete_file(session: Session, file_id: int) -> bool:
    file = session.query(File).filter(File.id == file_id).first()
    if file:
        session.delete(file)
        return True
    return False

