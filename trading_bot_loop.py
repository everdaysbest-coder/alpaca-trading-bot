"""
trading_bot_loop.py
====================
نسخة "دائمة التشغيل" من trading_bot.py، مخصصة للعمل على Render كخطة مجانية.
"""

import os
import time
import threading
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from trading_bot import main as run_trading_cycle

CHECK_INTERVAL_MINUTES = 15
PORT = int(os.environ.get("PORT", 10000))


class HealthCheckHandler(BaseHTTPRequestHandler):
    """سيرفر بسيط بيرد بـ OK على GET و HEAD، مع Content-Length صريح."""

    def _respond(self, send_body: bool):
        body = b"Alpaca trading bot worker is alive."
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def do_GET(self):
        self._respond(send_body=True)

    def do_HEAD(self):
        self._respond(send_body=False)

    def log_message(self, format, *args):
        pass


def is_market_hours() -> bool:
    now = datetime.now(timezone.utc)
    if now.weekday() >= 5:
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
    t = threading.Thread(target=trading_loop, daemon=True)
    t.start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    print(f"🌐 سيرفر فحص الصحة شغال على البورت {PORT}")
    server.serve_forever()
