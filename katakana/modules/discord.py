# modules/discord.py

from __future__ import annotations
from typing import Optional, Type
from katakana.http import SessionManager, HttpRequest, HttpMethod
from dataclasses import dataclass, fields, asdict, is_dataclass
from typing import Any, Dict, TypeVar, Type
from enum import IntFlag, IntEnum

T = TypeVar('T', bound='BaseModel')

@dataclass
class BaseModel:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        field_names = {field.name for field in cls.__dataclass_fields__}  
        filtered_data = {k: v for k, v in data.items() if k in field_names}  
        return cls(**filtered_data) 

    @staticmethod
    def _is_dataclass_instance(obj):
        return is_dataclass(obj) and not isinstance(obj, type)
    
class UserFlags(IntFlag):
    STAFF = 1 << 0
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSEUDO_USER = 1 << 10
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19
    ACTIVE_DEVELOPER = 1 << 22

    @classmethod
    def get_flag_names(cls, value: int) -> list[str]:
        return [flag.name for flag in cls if flag in UserFlags(value)]

class PremiumTypes(IntEnum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
    NITRO_BASIC = 3

    @classmethod
    def get_premium_name(cls, value: int) -> str:
        return cls(value).name if value in cls._value2member_map_ else "Unknown"

@dataclass
class DiscordUser(BaseModel):
    id: str
    username: str
    discriminator: str
    avatar: Optional[str] = None
    bot: bool = False
    system: bool = False
    mfa_enabled: bool = False
    banner: Optional[str] = None
    accent_color: Optional[int] = None
    locale: Optional[str] = None
    verified: bool = False
    email: Optional[str] = None
    flags: Optional[int] = None
    premium_type: Optional[int] = None
    public_flags: Optional[int] = None
    global_name: Optional[str] = None
    avatar_decoration_data: Optional[str] = None
    banner_color: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiscordUser':
        field_names = {field.name for field in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)
    
    def get_flag_texts(self) -> list[str]:
        if self.flags is not None:
            return UserFlags.get_flag_names(self.flags)
        return []
    
    def get_premium_type_text(self) -> str:
        if self.premium_type is not None:
            return PremiumTypes.get_premium_name(self.premium_type)
        return "None"
    
class DiscordClient:
    BASE_URL = "https://discord.com/api/users/"

    def __init__(self, token: str):
        self.session_manager = SessionManager()
        self.session = self.session_manager.get_session()
        self.token = token

    def get_user_info(self, user_id: int) -> Optional[DiscordUser]:
        headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        request = HttpRequest(
            method=HttpMethod.GET,
            url=f"{self.BASE_URL}{user_id}",
            headers=headers
        )
        response = request.send(self.session)
        if response.status_code == 200:
            return DiscordUser.from_dict(response.body)
        else:
            return None

