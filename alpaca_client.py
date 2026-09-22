"""
alpaca_client.py
==================
غلاف بسيط لكل استدعاءات Alpaca API التي نحتاجها:
معلومات الحساب، الصفقات المفتوحة، بيانات الأسعار التاريخية، الأخبار، وتنفيذ الأوامر.

🔧 إصلاح مؤكد (موثّق من مصدر رسمي Alpaca): بدون 'start' صريح، الـ API تفترض
start = بداية اليوم الحالي — يعني نستلم شمعة واحدة أو صفر، بغض النظر عن قيمة
'limit'. هذا كان يخلي كل حساب متوسط متحرك يفشل (يرجع None) دايمًا، فالإشارة
الفنية تطلع 'neutral' لكل الأسهم بلا استثناء.
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
    """يرجع أسعار الإغلاق اليومية الأخيرة لسهم أو عملة مشفرة معينة.
    نحدد 'start' صراحة (هامش أمان +10 أيام إضافية لتغطية عطل نهاية الأسبوع/الأسواق
    المغلقة) — بدونها Alpaca تفترض بداية اليوم الحالي بس، فما ترجع بيانات كافية."""
    is_crypto = "/" in symbol  # مثال: BTC/USD
    start = (datetime.now(timezone.utc) - timedelta(days=days + 10)).strftime("%Y-%m-%dT%H:%M:%SZ")

    if is_crypto
