# katakana/http.py

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Type
from requests import Session, Response

class HttpMethod(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    PATCH = auto()

@dataclass
class BaseModel:
    @classmethod
    def from_dict(cls: Type[BaseModel], data: Dict[str, Any]) -> BaseModel:
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class HttpRequest(BaseModel):
    method: HttpMethod
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None

    def send(self, session: Session) -> HttpResponse:
        request_method = self.method.name.lower()
        response = session.request(
            method=request_method,
            url=self.url,
            headers=self.headers,
            params=self.params,
            data=self.data,
            json=self.json
        )
        return HttpResponse.from_response(response)

@dataclass
class HttpResponse(BaseModel):
    status_code: int
    headers: Dict[str, str]
    body: Any

    @classmethod
    def from_response(cls: Type[HttpResponse], response: Response) -> HttpResponse:
        return cls(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
        )

class SessionManager:
    _session: Optional[Session] = None

    @classmethod
    def get_session(cls) -> Session:
        if cls._session is None:
            cls._session = Session()
        return cls._session

