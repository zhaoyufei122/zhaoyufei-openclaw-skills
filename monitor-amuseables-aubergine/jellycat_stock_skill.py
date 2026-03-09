import argparse
import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


DEFAULT_URL = "https://jellycat.com/vivacious-vegetable-aubergine/"
DEFAULT_STATE_FILE = ".amuseables_aubergine_state.json"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)


@dataclass
class StockSnapshot:
    checked_at: str
    url: str
    page_in_stock: bool | None
    small_in_stock: bool | None
    large_in_stock: bool | None
    blocked: bool
    raw_labels: list[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def parse_bool_from_text(value: str) -> bool | None:
    cleaned = normalize_text(value)
    if not cleaned:
        return None

    positive_tokens = ["in stock", "available", "add to cart", "buy now"]
    negative_tokens = ["sold out", "out of stock", "unavailable", "notify me"]

    if any(token in cleaned for token in positive_tokens):
        return True
    if any(token in cleaned for token in negative_tokens):
        return False
    return None


def is_challenge_page(html: str) -> bool:
    lowered = html.lower()
    markers = [
        "just a moment",
        "challenge-platform",
        "cf_chl_",
        "enable javascript and cookies to continue",
        "cloudflare",
    ]
    return any(marker in lowered for marker in markers)


def parse_variant_stock_from_json(data: Any) -> dict[str, bool | None]:
    result = {"small": None, "large": None}

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            name = normalize_text(str(node.get("name", "")))
            stock_flag = None

            if "availability" in node:
                avail = str(node.get("availability", "")).lower()
                if "instock" in avail:
                    stock_flag = True
                elif "outofstock" in avail:
                    stock_flag = False
            elif "available" in node:
                value = node.get("available")
                if isinstance(value, bool):
                    stock_flag = value
                elif isinstance(value, str):
                    stock_flag = parse_bool_from_text(value)

            if name and stock_flag is not None:
                if "small" in name:
                    result["small"] = stock_flag
                if "large" in name:
                    result["large"] = stock_flag

            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(data)
    return result


def parse_page_stock(html: str, url: str) -> StockSnapshot:
    if is_challenge_page(html):
        return StockSnapshot(
            checked_at=now_iso(),
            url=url,
            page_in_stock=None,
            small_in_stock=None,
            large_in_stock=None,
            blocked=True,
            raw_labels=["cloudflare challenge page detected"],
        )

    soup = BeautifulSoup(html, "html.parser")

    small_status: bool | None = None
    large_status: bool | None = None
    page_status: bool | None = None
    labels: list[str] = []

    json_scripts = soup.select('script[type="application/ld+json"], script[type="application/json"]')
    for script in json_scripts:
        text = script.string or script.get_text(strip=True)
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue

        variant_status = parse_variant_stock_from_json(payload)
        if small_status is None:
            small_status = variant_status["small"]
        if large_status is None:
            large_status = variant_status["large"]

        if page_status is None and any(v is not None for v in variant_status.values()):
            if any(v is True for v in variant_status.values()):
                page_status = True
            elif all(v is False for v in variant_status.values() if v is not None):
                page_status = False

    candidate_texts: list[str] = []
    for element in soup.find_all(["button", "span", "div", "p", "label", "option", "li"]):
        text = element.get_text(" ", strip=True)
        normalized = normalize_text(text)
        if not normalized:
            continue
        if any(keyword in normalized for keyword in ["stock", "sold out", "out of stock", "available", "add to cart", "notify me", "small", "large"]):
            candidate_texts.append(normalized)

    deduped = []
    for item in candidate_texts:
        if item not in deduped:
            deduped.append(item)
    labels.extend(deduped[:100])

    for text in deduped:
        compact = normalize_text(text)
        if "small" in compact and small_status is None:
            small_status = parse_bool_from_text(compact)
        if "large" in compact and large_status is None:
            large_status = parse_bool_from_text(compact)

    page_text = normalize_text(soup.get_text(" ", strip=True))
    if page_status is None:
        page_status = parse_bool_from_text(page_text)

    if page_status is None:
        if small_status is True or large_status is True:
            page_status = True
        elif small_status is False and large_status is False:
            page_status = False

    return StockSnapshot(
        checked_at=now_iso(),
        url=url,
        page_in_stock=page_status,
        small_in_stock=small_status,
        large_in_stock=large_status,
        blocked=False,
        raw_labels=labels,
    )


def load_previous_state(state_file: Path) -> StockSnapshot | None:
    if not state_file.exists():
        return None
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        data.setdefault("blocked", False)
        return StockSnapshot(**data)
    except Exception:
        return None


def save_state(state_file: Path, snapshot: StockSnapshot) -> None:
    state_file.write_text(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2), encoding="utf-8")


def snapshot_changed(previous: StockSnapshot | None, current: StockSnapshot) -> bool:
    if previous is None:
        return True
    return (
        previous.page_in_stock != current.page_in_stock
        or previous.small_in_stock != current.small_in_stock
        or previous.large_in_stock != current.large_in_stock
        or previous.blocked != current.blocked
    )


def notify(message: str, webhook_url: str | None) -> None:
    print(message)
    if webhook_url:
        try:
            requests.post(webhook_url, json={"text": message}, timeout=10)
        except Exception as error:
            print(f"[WARN] Webhook failed: {error}")


def fetch_html(url: str, timeout: int = 15) -> str:
    session = requests.Session()
    session.headers.update({
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    })
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def pretty_state(snapshot: StockSnapshot) -> str:
    def fmt(value: bool | None) -> str:
        if value is True:
            return "IN_STOCK"
        if value is False:
            return "OUT_OF_STOCK"
        return "UNKNOWN"

    if snapshot.blocked:
        return f"[{snapshot.checked_at}] BLOCKED_BY_ANTIBOT | url={snapshot.url}"

    return (
        f"[{snapshot.checked_at}] page={fmt(snapshot.page_in_stock)} | "
        f"small={fmt(snapshot.small_in_stock)} | large={fmt(snapshot.large_in_stock)}"
    )


def run_once(url: str, state_file: Path, webhook_url: str | None, always_notify: bool) -> None:
    html = fetch_html(url)
    current = parse_page_stock(html, url)

    previous = load_previous_state(state_file)
    changed = snapshot_changed(previous, current)

    if current.blocked:
        prefix = "[BLOCKED]"
        notify(f"{prefix} {pretty_state(current)}", webhook_url if always_notify else None)
    elif changed or always_notify:
        prefix = "[CHANGE]" if changed else "[CHECK]"
        notify(f"{prefix} {pretty_state(current)}", webhook_url)
    else:
        print(f"[NO_CHANGE] {pretty_state(current)}")

    save_state(state_file, current)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor Jellycat Amuseables Aubergine stock.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Product URL")
    parser.add_argument("--interval", type=int, default=300, help="Polling interval in seconds")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE, help="Path to local state JSON")
    parser.add_argument("--webhook-url", default=None, help="Optional webhook URL for notifications")
    parser.add_argument("--always-notify", action="store_true", help="Notify every check")
    parser.add_argument("--once", action="store_true", help="Run one check and exit")

    args = parser.parse_args()
    state_path = Path(args.state_file)

    if args.once:
        run_once(args.url, state_path, args.webhook_url, args.always_notify)
        return

    while True:
        try:
            run_once(args.url, state_path, args.webhook_url, args.always_notify)
        except Exception as error:
            print(f"[ERROR] {now_iso()} {error}")
        time.sleep(max(args.interval, 30))


if __name__ == "__main__":
    main()
