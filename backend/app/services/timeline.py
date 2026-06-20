from __future__ import annotations

import re
from datetime import date, datetime


DATE_PATTERNS = [
    re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})"),
    re.compile(r"(?P<date>\d{1,2}/\d{1,2}/\d{4})"),
]


def _parse_date(value: str) -> date | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(value)
        if not match:
            continue
        date_text = match.group("date")
        try:
            if "-" in date_text:
                return datetime.strptime(date_text, "%Y-%m-%d").date()
            return datetime.strptime(date_text, "%m/%d/%Y").date()
        except ValueError:
            return None
    return None


def generate_timeline_entries(extracted_text: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for raw_line in extracted_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        event_date = _parse_date(line)
        if len(line) < 12:
            continue
        entries.append({"event_text": line[:500], "event_date": event_date})
    return entries[:100]
