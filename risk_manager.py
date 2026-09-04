"""
risk_manager.py
================
كل قواعد إدارة المخاطرة في مكان واحد: حجم الصفقة، حدود عدد الصفقات،
والقاطع الدائري اليومي (Daily Circuit Breaker) الذي يوقف الشراء لو تجاوزت
الخسارة اليومية الحد المسموح.
"""

import json
import os
from datetime import date

from config import (
    MAX_POSITION_PCT, STOP_LOSS_PCT, TAKE_PROFIT_PCT,
    MAX_OPEN_POSITIONS, DAILY_LOSS_LIMIT_PCT,
)

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_state.json")


def _load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {}


def _save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_daily_circuit_breaker(current_equity: float) -> bool:
    """يرجع True لو مسموح الاستمرار بالتداول، False لو تجاوزنا حد الخسارة اليومي.
    يسجّل قيمة الحساب في بداية كل يوم تلقائيًا لأول تشغيل في ذلك اليوم."""
    today = date.today().isoformat()
    state = _load_state()

    if state.get("date") != today:
        state = {"date": today, "starting_equity": current_equity}
        _save_state(state)
        return True

    starting_equity = state.get("starting_equity", current_equity)
    if starting_equity <= 0:
        return True

    loss_pct = (starting_equity - current_equity) / starting_equity
    if loss_pct >= DAILY_LOSS_LIMIT_PCT:
        print(f"   🛑 قاطع الدائرة اليومي فعّال: خسارة {loss_pct:.1%} تجاوزت الحد المسموح {DAILY_LOSS_LIMIT_PCT:.0%}")
        return False
    return True


def can_open_new_position(open_positions_count: int) -> bool:
    return open_positions_count < MAX_OPEN_POSITIONS


def calculate_position(buying_power: float, current_price: float) -> dict:
    """يحسب حجم الصفقة وأسعار وقف الخسارة وجني الأرباح."""
    position_value = buying_power * MAX_POSITION_PCT
    qty = int(position_value // current_price)
    stop_loss_price = current_price * (1 - STOP_LOSS_PCT)
    take_profit_price = current_price * (1 + TAKE_PROFIT_PCT)
    return {
        "qty": qty,
        "stop_loss_price": stop_loss_price,
        "take_profit_price": take_profit_price,
    }
