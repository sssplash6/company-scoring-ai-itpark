from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from .storage import CacheStore
from .utils import normalize_whitespace, unique_list


USER_AGENT = "Mozilla/5.0 (compatible; ITParkScoringBot/0.1; +https://itpark.local)"


@dataclass
class Page:
    url: str
    content: str
    fetched_at: datetime


class PublicCollector:
    def __init__(self, cache: CacheStore, timeout: int = 15):
        self.cache = cache
        self.timeout = timeout

    def search_company(self, name: str, max_results: int = 5) -> List[str]:
        query = f"{name} company website"
        url = "https://duckduckgo.com/html/"
        params = {"q": query}
        headers = {"User-Agent": USER_AGENT}
        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        except requests.RequestException:
            return []
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "lxml")
        candidates = []
        for link in soup.select("a.result__a"):
            href = link.get("href", "")
            if not href:
                continue
            if "duckduckgo.com/l/" in href:
                parsed = urlparse(href)
                qs = parse_qs(parsed.query)
                if "uddg" in qs:
                    href = qs["uddg"][0]
            candidates.append(href)
        filtered = []
        for href in candidates:
            parsed = urlparse(href)
            if not parsed.scheme.startswith("http"):
                continue
            filtered.append(href)
        return unique_list(filtered)[:max_results]

    def resolve_candidates(self, name: str, provided_website: Optional[str]) -> List[str]:
        if provided_website:
            return [self._normalize_url(provided_website)]
        results = self.search_company(name)
        return results

    def _normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        if not parsed.scheme:
            return f"https://{url}"
        return url

    def _can_fetch(self, base_url: str, target_url: str) -> bool:
        robots_url = urljoin(base_url, "/robots.txt")
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            parser.read()
        except Exception:
            return True
        return parser.can_fetch(USER_AGENT, target_url)

    def fetch_page(self, url: str) -> Optional[Page]:
        cached = self.cache.get_page(url)
        if cached:
            return Page(url=url, content=cached, fetched_at=datetime.utcnow())
        headers = {"User-Agent": USER_AGENT}
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
        except requests.RequestException:
            return None
        if response.status_code != 200:
            return None
        content = response.text
        self.cache.save_page(url, content)
        return Page(url=url, content=content, fetched_at=datetime.utcnow())

    def discover_pages(self, base_url: str, homepage_html: str, limit: int = 8) -> List[str]:
        soup = BeautifulSoup(homepage_html, "lxml")
        keywords = [
            "about",
            "services",
            "solutions",
            "expertise",
            "portfolio",
            "case",
            "clients",
            "industries",
            "contact",
            "careers",
            "jobs",
            "security",
            "privacy",
            "compliance",
            "certification",
        ]
        links = []
        for a in soup.select("a[href]"):
            href = a.get("href")
            text = normalize_whitespace(a.get_text(" "))
            if not href:
                continue
            if href.startswith("#"):
                continue
            full = urljoin(base_url, href)
            label = f"{href} {text}".lower()
            if any(k in label for k in keywords):
                links.append(full)
        return unique_list(links)[:limit]

    def collect_company(self, base_url: str, extra_pages: Optional[List[str]] = None) -> List[Page]:
        base_url = self._normalize_url(base_url)
        if not self._can_fetch(base_url, base_url):
            return []
        pages = []
        homepage = self.fetch_page(base_url)
        if not homepage:
            return []
        pages.append(homepage)
        links = self.discover_pages(base_url, homepage.content)
        if extra_pages:
            links.extend(extra_pages)
        links = unique_list(links)
        for link in links:
            if not self._can_fetch(base_url, link):
                continue
            time.sleep(0.5)
            page = self.fetch_page(link)
            if page:
                pages.append(page)
        return pages
