"""
alpaca_client.py
==================
غلاف بسيط لكل استدعاءات Alpaca API التي نحتاجها:
معلومات الحساب، الصفقات المفتوحة، بيانات الأسعار التاريخية، الأخبار، وتنفيذ الأوامر.

🔧 إصلاح مؤكد (موثّق من مصدر رسمي Alpaca): بدون 'start' صريح، الـ API تفترض
start = بداية اليوم الحالي — يعني نستلم شمعة واحدة أو صفر، بغض النظر عن قيمة
'limit'. هذا كان يخلي كل حساب متوسط متحرك يفشل (يرجع None) دايمًا.
"""

from datetime import datetime, timedelta, timezone

import requests

from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, ALPACA_DATA_URL

HEADERS = {
    "APCA-API-KEY-ID": ALPACA_API_KEY,
    "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
}


def get_account() -> dict:
    r = requests.get(f"{ALPACA_BASE_URL}/v2/account", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def get_open_positions() -> list:
    r = requests.get(f"{ALPACA_BASE_URL}/v2/positions", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def get_recent_bars(symbol: str, days: int = 30) -> list:
    """يرجع أسعار الإغلاق اليومية الأخيرة لسهم أو عملة مشفرة معينة."""
    is_crypto = "/" in symbol
    start = (datetime.now(timezone.utc) - timedelta(days=days + 10)).strftime("%Y-%m-%dT%H:%M:%SZ")

    if is_crypto:
        r = requests.get(
            f"{ALPACA_DATA_URL}/v1beta3/crypto/us/bars",
            headers=HEADERS,
            params={"symbols": symbol, "timeframe": "1Day", "start": start, "limit": days},
            timeout=15,
        )
        r.raise_for_status()
        bars = r.json().get("bars", {}).get(symbol) or []
    else:
        r = requests.get(
            f"{ALPACA_DATA_URL}/v2/stocks/{symbol}/bars",
            headers=HEADERS,
            params={"timeframe": "1Day", "start": start, "limit": days, "adjustment": "raw", "feed": "iex"},
            timeout=15,
        )
        r.raise_for_status()
        bars = r.json().get("bars") or []

    return [b["c"] for b in bars]


def get_recent_news(symbol: str, limit: int = 5) -> list:
    """يرجع عناوين آخر الأخبار المتعلقة بسهم معين."""
    r = requests.get(
        f"{ALPACA_DATA_URL}/v1beta1/news",
        headers=HEADERS,
        params={"symbols": symbol, "limit": limit, "sort": "desc"},
        timeout=15,
    )
    r.raise_for_status()
    news = r.json().get("news") or []
    return [item["headline"] for item in news]


def place_bracket_order(symbol: str, qty: int, entry_price: float, stop_loss_price: float, take_profit_price: float) -> dict:
    """يفتح صفقة شراء مع وقف خسارة وجني أرباح تلقائيين مرفقين معا (Bracket Order)."""
    order = {
        "symbol": symbol,
        "qty": str(qty),
        "side": "buy",
        "type": "market",
        "time_in_force": "day",
        "order_class": "bracket",
        "take_profit": {"limit_price": round(take_profit_price, 2)},
        "stop_loss": {"stop_price": round(stop_loss_price, 2)},
    }
    r = requests.post(f"{ALPACA_BASE_URL}/v2/orders", headers=HEADERS, json=order, timeout=15)
    r.raise_for_status()
    return r.json()
