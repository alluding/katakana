# modules/pypi.py

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from katakana.http import SessionManager
from bs4 import BeautifulSoup
import re

@dataclass
class GitHubRepoInfo:
    full_name: str
    description: Optional[str]
    clone_url: str
    stars: int
    forks: int
    open_issues: int
    language: Optional[str]

    @classmethod
    def from_github_api(cls, repo_owner: str, repo_name: str) -> 'GitHubRepoInfo':
        session = SessionManager.get_session()
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        response = session.get(url)
        data = response.json()
        return cls(
            full_name=data['full_name'],
            description=data.get('description'),
            clone_url=data['clone_url'],
            stars=data['stargazers_count'],
            forks=data['forks_count'],
            open_issues=data['open_issues_count'],
            language=data.get('language')
        )

@dataclass
class PyPIPackageInfo:
    name: str
    version: str
    release_date: Optional[str]
    github_info: Optional[GitHubRepoInfo] = None

    @staticmethod
    def extract_github_repo(url: str) -> Optional[GitHubRepoInfo]:
        if 'github.com' in url:
            parts = url.split('/')
            repo_owner, repo_name = parts[-2], parts[-1].replace('.git', '')
            return GitHubRepoInfo.from_github_api(repo_owner, repo_name)
        return None

    @classmethod
    def from_pypi(cls, package_name: str) -> 'PyPIPackageInfo':
        session = SessionManager.get_session()
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = session.get(url)
        if response.status_code != 200:
            return cls(name=package_name, version="Unknown", release_date=None)
        
        data = response.json()
        version = data['info']['version']
        release_date = data['releases'][version][0]['upload_time'] if version in data['releases'] else None
        github_info = None

        project_urls = data['info'].get('project_urls', {})
        for url in project_urls.values():
            github_info = cls.extract_github_repo(url)
            if github_info:
                break

        return cls(name=package_name, version=version, release_date=release_date, github_info=github_info)

@dataclass
class PyPIUserInfo:
    username: str
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    packages: List[Dict[str, str]] = field(default_factory=list) 
    description: Optional[str] = None
    joined_date: Optional[str] = None

    @staticmethod
    def _extract_email(soup: BeautifulSoup) -> Optional[str]:
        email_element = soup.find('a', href=re.compile(r'^mailto:'))
        return email_element.get('href').replace('mailto:', '') if email_element else None
    
    @staticmethod
    def _extract_avatar_url(soup: BeautifulSoup) -> Optional[str]:
        avatar_element = soup.find('img', alt=re.compile(r'^Avatar for'))
        return avatar_element['src'] if avatar_element else None

    @staticmethod
    def _extract_joined_date(soup: BeautifulSoup) -> Optional[str]:
        joined_element = soup.find('time', {'data-controller': 'localized-time'})
        return joined_element['datetime'] if joined_element else None

    @classmethod
    def from_username(cls, username: str) -> 'PyPIUserInfo':
        session = SessionManager.get_session()
        url = f"https://pypi.org/user/{username}/"
        response = session.get(url)
        if response.status_code != 200:
            return cls(username=username)

        soup = BeautifulSoup(response.text, 'html.parser')
        profile = cls(
            username=username,
            avatar_url=cls._extract_avatar_url(soup),
            email=cls._extract_email(soup),
            description=cls._extract_description(soup),
            joined_date=cls._extract_joined_date(soup),
            packages=cls._parse_package_elements(soup)
        )

        return profile

    @staticmethod
    def _extract_description(soup: BeautifulSoup) -> Optional[str]:
        description_element = soup.find('p', {'class': 'description__content'})
        return description_element.get_text(strip=True) if description_element else None

    @staticmethod
    def _parse_package_elements(soup: BeautifulSoup) -> List[Dict[str, str]]:
        packages = []
        for package_element in soup.find_all('a', {'class': 'package-snippet'}):
            name = package_element.find('h3', {'class': 'package-snippet__title'}).get_text(strip=True)
            released = package_element.find('time', {'data-controller': 'localized-time'}).get_text(strip=True)
            description = package_element.find('p', {'class': 'package-snippet__description'}).get_text(strip=True).strip()
            packages.append({
                'name': name,
                'released': released,
                'desc': description
            })
        return packages
