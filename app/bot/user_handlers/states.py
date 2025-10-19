from enum import Enum
from dataclasses import dataclass


class UserState(Enum):
    FILLING_FULL_NAME = "filling_full_name"
    FILLING_COMPANY = "filling_company"
    FILLING_POSITION = "filling_position"
    FILLING_PHONE = "filling_phone"
    MATERIAL_REQUESTED = "material_requested"


@dataclass
class UserContext:
    state: UserState | None = None
    pending_material_id: int | None = None
    profile_menu_message_id: int | None = None
    request_message_id: int | None = None


user_contexts: dict[int, UserContext] = {}
