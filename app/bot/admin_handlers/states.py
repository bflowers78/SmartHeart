from enum import Enum
from dataclasses import dataclass, field


class AdminState(Enum):
    FILLING_TITLE = "filling_title"
    FILLING_MESSAGE_TEXT = "filling_message_text"
    FILLING_PHOTO = "filling_photo"
    FILLING_DOCUMENT = "filling_document"


@dataclass
class AdminContext:
    state: AdminState | None = None
    category: str | None = None
    material_id: int | None = None
    menu_message_id: int | None = None
    request_message_id: int | None = None
    title: str | None = None
    message_text: str | None = None
    media_file_id: str | None = None
    document_file_ids: list[int] = field(default_factory=list)


admin_contexts: dict[int, AdminContext] = {}

