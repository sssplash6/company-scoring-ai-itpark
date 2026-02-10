from __future__ import annotations

import re
from typing import Iterable, List

from bs4 import BeautifulSoup


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text(" ")
    return normalize_whitespace(text)


def unique_list(items: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item.strip())
    return result
