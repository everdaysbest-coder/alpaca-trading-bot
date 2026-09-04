"""
trading_bot.py
==============
السكربت الرئيسي. يعمل مرة واحدة عند كل تشغيل (مصمّم كـ Cron Job قرب افتتاح السوق):

1. يتحقق من قاطع الدائرة اليومي (توقف لو الخسارة اليوم تجاوزت الحد)
2. يفحص كل سهم في WATCHLIST غير مملوك حاليًا
3. يحلل: زخم فني + مزاج الأخبار
4. لو الإشارتان متوافقتان، يفتح صفقة بحجم محسوب وبوقف خسارة/جني أرباح تلقائيين

⚠️ هذا نظام مخاطرة منخفضة، ليس ضمانًا للربح. لا يوجد تداول بدون مخاطرة.
"""

import sys

from alpaca_client import get_account, get_open_positions, get_recent_bars, get_recent_news, place_bracket_order
from analysis import should_buy
from config import WATCHLIST
from risk_manager import check_daily_circuit_breaker, can_open_new_position, calculate_position


def main():
    account = get_account()
    equity = float(account["equity"])
    buying_power = float(account["buying_power"])
    print(f"💰 قيمة الحساب: ${equity:,.2f} | القوة الشرائية: ${buying_power:,.2f}")

    if not check_daily_circuit_breaker(equity):
        print("توقف التداول لهذا اليوم بسبب قاطع الدائرة. لا صفقات جديدة.")
        return

    open_positions = get_open_positions()
    held_symbols = {p["symbol"] for p in open_positions}
    print(f"📊 صفقات مفتوحة حاليًا: {len(open_positions)} ({', '.join(held_symbols) or 'لا شيء'})")

    trades_opened = 0
    for symbol in WATCHLIST:
        if symbol in held_symbols:
            continue
        if not can_open_new_position(len(held_symbols) + trades_opened):
            print("🛑 وصلنا للحد الأقصى للصفقات المفتوحة المسموحة.")
            break

        print(f"🔍 فحص {symbol}...")
        prices = get_recent_bars(symbol)
        if not prices:
            print(f"   ⚠️ لا توجد بيانات أسعار كافية لـ {symbol}، تجاهل.")
            continue

        headlines = get_recent_news(symbol)
        buy, reason = should_buy(prices, symbol, headlines)
        print(f"   {reason}")

        if not buy:
            continue

        current_price = prices[-1]
        position = calculate_position(buying_power, current_price)
        if position["qty"] < 1:
            print(f"   ⚠️ حجم الصفقة المحسوب أقل من سهم واحد، تجاهل {symbol}.")
            continue

        order = place_bracket_order(
            symbol, position["qty"], current_price,
            position["stop_loss_price"], position["take_profit_price"],
        )
        print(f"   ✅ فُتحت صفقة: {position['qty']} سهم {symbol} عند ~${current_price:.2f} "
              f"(وقف خسارة ${position['stop_loss_price']:.2f}, جني أرباح ${position['take_profit_price']:.2f})")
        trades_opened += 1

    print(f"🏁 انتهى الفحص. صفقات جديدة فُتحت: {trades_opened}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ فشل: {e}", file=sys.stderr)
        sys.exit(1)
