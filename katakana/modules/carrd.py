# modules/card.py

from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import List, Optional
from katakana.http import SessionManager

@dataclass
class CarrdProfile:
    profile_url: str
    links: List[str] = field(default_factory=list)
    name: Optional[str] = None
    about_me: Optional[str] = None
    other_text: List[str] = field(default_factory=list)

    @classmethod
    def from_url(cls, url: str) -> 'CarrdProfile':
        response = SessionManager.get_session().get(url)
        if response.status_code != 200:
            return cls(profile_url=url)  
        soup = BeautifulSoup(response.text, 'html.parser')
        profile = cls(
            profile_url=url.replace("https://", ""),
            links=[link['href'] for link in soup.find_all('a', href=True) if link['href'].startswith('http')],
            name=soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3'] and tag.get('class', '') == 'name', None),
            about_me=soup.find(lambda tag: tag.name in ['p', 'div'] and tag.get('class', '') == 'about', None),
            other_text=[element.get_text(strip=True) for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])]
        )
        profile.name = profile.name.get_text(strip=True) if profile.name else None
        profile.about_me = profile.about_me.get_text(strip=True) if profile.about_me else None
        return profile

def lookup_carrd_profile(name: str) -> Optional[CarrdProfile]:
    if not name.strip():
        return None  
    return CarrdProfile.from_url(f"https://{name}.carrd.co")
