"""
trading_bot_loop.py
====================
نسخة "دائمة التشغيل" من trading_bot.py، مخصصة للعمل على Render كخطة مجانية.

ملاحظة تقنية مهمة:
Render "Free Web Service" محتاج السيرفر يفتح بورت (عشان يعتبره صحي)، بعكس
"Background Worker" اللي بيكلف $7/شهر. الحل: نفتح سيرفر HTTP بسيط جدًا في
Thread منفصل (بيرد بس "OK")، وفي نفس الوقت نشغّل حلقة فحص السوق في الخلفية.

بعد الرفع، لازم تضيف "cronjob" جديد على cron-job.org بيزور رابط السيرفر ده
كل 10-14 دقيقة، بنفس الطريقة اللي عملناها مع cinemora-backend، عشان يفضل صاحي
ومايناموش بعد 15 دقيقة سكون.
"""

import os
import time
import threading
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

from trading_bot import main as run_trading_cycle

CHECK_INTERVAL_MINUTES = 15
PORT = int(os.environ.get("PORT", 10000))


class HealthCheckHandler(BaseHTTPRequestHandler):
    """سيرفر بسيط جدًا بيرد بـ OK بس، عشان Render يعتبر الخدمة صحية."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Alpaca trading bot worker is alive.")

    def log_message(self, format, *args):
        pass  # نمنع طباعة كل طلب HTTP عشان اللوجز تفضل نضيفة


def is_market_hours() -> bool:
    """فحص تقريبي لساعات تداول أمريكا (14:30 - 21:00 UTC، أيام الأسبوع فقط)."""
    now = datetime.now(timezone.utc)
    if now.weekday() >= 5:  # السبت=5, الأحد=6
        return False
    minutes_since_midnight = now.hour * 60 + now.minute
    return 14 * 60 + 30 <= minutes_since_midnight <= 21 * 60


def trading_loop():
    print(f"🚀 بدء حلقة فحص السوق — كل {CHECK_INTERVAL_MINUTES} دقيقة")
    while True:
        try:
            if is_market_hours():
                print(f"\n⏰ {datetime.now(timezone.utc).isoformat()} — تشغيل دورة فحص جديدة...")
                run_trading_cycle()
            else:
                print(f"😴 {datetime.now(timezone.utc).isoformat()} — خارج ساعات التداول، تخطي الفحص")
        except Exception as e:
            print(f"❌ خطأ غير متوقع أثناء التشغيل: {e}")
            traceback.print_exc()

        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    # نشغّل حلقة فحص السوق في Thread منفصل بالخلفية
    t = threading.Thread(target=trading_loop, daemon=True)
    t.start()

    # ونفتح سيرفر HTTP بسيط في الـ Thread الرئيسي عشان Render يقبل الخدمة كـ Web Service مجاني
    server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    print(f"🌐 سيرفر فحص الصحة شغال على البورت {PORT}")
    server.serve_forever()
