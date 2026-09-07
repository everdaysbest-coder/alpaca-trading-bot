"""
trading_bot_loop.py
====================
نسخة "دائمة التشغيل" من trading_bot.py، مخصصة للعمل على Render كـ Background Worker
بدل GitHub Actions. بتنادي نفس دالة main() الموجودة في trading_bot.py كل فترة
زمنية محددة، وتفضل شغالة طول ما السيرفر شغال (24/7).

الفرق عن trading_bot.py الأصلي:
- trading_bot.py: يشتغل مرة واحدة ويخرج (مناسب لـ GitHub Actions Cron)
- trading_bot_loop.py: يفضل شغال في حلقة لا نهائية (مناسب لسيرفر دائم زي Render)
"""

import time
import traceback
from datetime import datetime, timezone

from trading_bot import main as run_trading_cycle

# كل قد إيه (بالدقايق) نعيد فحص السوق
CHECK_INTERVAL_MINUTES = 15


def is_market_hours() -> bool:
    """فحص تقريبي لساعات تداول أمريكا (14:30 - 21:00 UTC، أيام الأسبوع فقط)."""
    now = datetime.now(timezone.utc)
    if now.weekday() >= 5:  # السبت=5, الأحد=6
        return False
    minutes_since_midnight = now.hour * 60 + now.minute
    return 14 * 60 + 30 <= minutes_since_midnight <= 21 * 60


def main_loop():
    print(f"🚀 بدء تشغيل trading_bot_loop.py — سيفحص السوق كل {CHECK_INTERVAL_MINUTES} دقيقة")
    while True:
        try:
            if is_market_hours():
                print(f"\n⏰ {datetime.now(timezone.utc).isoformat()} — تشغيل دورة فحص جديدة...")
                run_trading_cycle()
            else:
                print(f"😴 {datetime.now(timezone.utc).isoformat()} — خارج ساعات التداول، تخطي الفحص (الأسهم فقط، الكريبتو 24/7 وممكن نشغله دايمًا لو حبيت)")
        except Exception as e:
            print(f"❌ خطأ غير متوقع أثناء التشغيل: {e}")
            traceback.print_exc()

        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main_loop()

