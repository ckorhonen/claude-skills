#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Any, Dict, Optional, Tuple


LIMITS: Dict[str, Dict[str, int]] = {
    "ios": {
        "app_name": 30,
        "subtitle": 30,
        "promotional_text": 170,
        "keywords": 100,
        "description": 4000,
        "whats_new": 4000,
    },
    "google_play": {
        "title": 30,
        "short_description": 80,
        "full_description": 4000,
    },
}


ALIASES: Dict[str, str] = {
    "name": "app_name",
    "appname": "app_name",
    "app_name": "app_name",
    "subtitle": "subtitle",
    "promo": "promotional_text",
    "promotionaltext": "promotional_text",
    "promotional_text": "promotional_text",
    "keywords": "keywords",
    "keyword": "keywords",
    "desc": "description",
    "description": "description",
    "whatsnew": "whats_new",
    "what_s_new": "whats_new",
    "whats_new": "whats_new",
    "title": "title",
    "shortdesc": "short_description",
    "short_description": "short_description",
    "fulldesc": "full_description",
    "full_description": "full_description",
}


def _normalize_key(key: str) -> str:
    normalized = key.strip().lower().replace("-", "_").replace(" ", "_")
    return ALIASES.get(normalized, normalized)


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "\n".join(str(item) for item in value)
    return str(value)


def _load_json(path: str) -> Dict[str, Any]:
    try:
        if path == "-":
            data = json.load(sys.stdin)
        else:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {exc}")

    if not isinstance(data, dict):
        raise SystemExit("Expected a JSON object mapping fields -> text.")
    return data


def _format_row(field: str, chars: int, limit: Optional[int]) -> Tuple[str, bool]:
    if limit is None:
        return (f"{field:<20} {chars:>5} {'-':>5}  n/a", False)
    if chars <= limit:
        return (f"{field:<20} {chars:>5} {limit:>5}  OK", False)
    over = chars - limit
    return (f"{field:<20} {chars:>5} {limit:>5}  OVER by {over}", True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check common App Store / Google Play character limits from a JSON object.",
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=sorted(LIMITS.keys()),
        help="Which limits to apply.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to JSON file, or '-' to read from stdin.",
    )
    args = parser.parse_args()

    limits = LIMITS[args.platform]
    data = _load_json(args.input)

    exceeded_any = False
    print(f"Platform: {args.platform}\n")
    print(f"{'field':<20} {'chars':>5} {'limit':>5}  status")
    print("-" * 44)
    for key, value in data.items():
        field = _normalize_key(str(key))
        text = _coerce_text(value).replace("\r\n", "\n")
        chars = len(text)
        limit = limits.get(field)
        line, exceeded = _format_row(field, chars, limit)
        exceeded_any = exceeded_any or exceeded
        print(line)

    return 1 if exceeded_any else 0


if __name__ == "__main__":
    raise SystemExit(main())
