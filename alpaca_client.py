"""
alpaca_client.py
=================
غلاف بسيط لكل استدعاءات Alpaca API التي نحتاجها:
معلومات الحساب، الصفقات المفتوحة، بيانات الأسعار التاريخية، الأخبار، وتنفيذ الأوامر.
"""

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
    """يرجع أسعار الإغلاق اليومية الأخيرة لسهم معيّن."""
    r = requests.get(
        f"{ALPACA_DATA_URL}/v2/stocks/{symbol}/bars",
        headers=HEADERS,
        params={"timeframe": "1Day", "limit": days, "adjustment": "raw"},
        timeout=15,
    )
    r.raise_for_status()
    bars = r.json().get("bars", [])
    return [b["c"] for b in bars]  # أسعار الإغلاق فقط


def get_recent_news(symbol: str, limit: int = 5) -> list:
    """يرجع عناوين آخر الأخبار المتعلقة بسهم معيّن."""
    r = requests.get(
        f"{ALPACA_DATA_URL}/v1beta1/news",
        headers=HEADERS,
        params={"symbols": symbol, "limit": limit, "sort": "desc"},
        timeout=15,
    )
    r.raise_for_status()
    news = r.json().get("news", [])
    return [item["headline"] for item in news]


def place_bracket_order(symbol: str, qty: int, entry_price: float, stop_loss_price: float, take_profit_price: float) -> dict:
    """يفتح صفقة شراء مع وقف خسارة وجني أرباح تلقائيين مرفقين معًا (Bracket Order)."""
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
