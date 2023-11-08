# core/loader.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union, Type, TypeVar
from katakana.modules.pypi import PyPIUserInfo, PyPIPackageInfo
from katakana.modules.discord import DiscordClient
from katakana.modules.carrd import CarrdProfile, lookup_carrd_profile
from enum import Enum, auto

T = TypeVar('T', PyPIUserInfo, PyPIPackageInfo, DiscordClient, CarrdProfile)

class LookupType(Enum):
    PYPI_USER = auto()
    PYPI_PACKAGE = auto()
    DISCORD_USER = auto()
    CARRD_USER = auto()

@dataclass
class LookupRunner:
    discord_token: Optional[str] = None
    discord_client: DiscordClient = field(init=False)

    def __post_init__(self):
        self.discord_client = DiscordClient(token=self.discord_token)

    @staticmethod
    def _lookup_user_info(query: str) -> PyPIUserInfo:
        return PyPIUserInfo.from_username(query)

    @staticmethod
    def _lookup_package_info(query: str) -> PyPIPackageInfo:
        return PyPIPackageInfo.from_pypi(query)
    
    @staticmethod
    def _lookup_carrd_user(query: str) -> CarrdProfile:
        return lookup_carrd_profile(query)

    def _lookup_discord_user(self, query: int) -> DiscordClient:
        return self.discord_client.get_user_info(query)
        
    def run_lookup(self, lookup_type: LookupType, query: Union[str, int]) -> Optional[T]:
        lookup_method: dict[LookupType, Type[Union[Type[LookupRunner], DiscordClient]]] = {
            LookupType.PYPI_USER: self._lookup_user_info,
            LookupType.PYPI_PACKAGE: self._lookup_package_info,
            LookupType.DISCORD_USER: self._lookup_discord_user,
            LookupType.CARRD_USER: self._lookup_carrd_user
        }

        if lookup_type in lookup_method and isinstance(query, (str, int)):
            return lookup_method[lookup_type](query)
        else:
            raise ValueError("Invalid lookup type or query")
