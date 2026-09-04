"""
notifier.py
===========
يرسل بريدًا إلكترونيًا عبر Resend، فقط عندما تُفتح صفقة فعلية
(وليس تقريرًا لكل تشغيل، حتى لا تُغرق بريدك برسائل غير ضرورية).

يحتاج:
  RESEND_API_KEY  - من resend.com (الطبقة المجانية كافية)
  NOTIFY_EMAIL    - البريد الذي يستقبل الإشعارات
"""

import os

import requests

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")

# نطاق الإرسال الافتراضي لـ Resend بدون الحاجة لربط دومين خاص
FROM_ADDRESS = "Alpaca Trading Bot <onboarding@resend.dev>"


def send_trade_email(symbol: str, qty: int, entry_price: float, stop_loss_price: float, take_profit_price: float) -> None:
    if not RESEND_API_KEY or not NOTIFY_EMAIL:
        print("   ℹ️ إعدادات البريد غير مضافة، تخطي إرسال الإشعار.")
        return

    subject = f"✅ صفقة جديدة: {qty} سهم {symbol}"
    body_html = f"""
    <h2>فُتحت صفقة جديدة</h2>
    <ul>
      <li><b>السهم:</b> {symbol}</li>
      <li><b>الكمية:</b> {qty}</li>
      <li><b>سعر الدخول:</b> ${entry_price:.2f}</li>
      <li><b>وقف الخسارة:</b> ${stop_loss_price:.2f}</li>
      <li><b>جني الأرباح:</b> ${take_profit_price:.2f}</li>
    </ul>
    """

    try:
        r = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": FROM_ADDRESS,
                "to": [NOTIFY_EMAIL],
                "subject": subject,
                "html": body_html,
            },
            timeout=15,
        )
        r.raise_for_status()
        print(f"   📧 أُرسل إشعار البريد لصفقة {symbol}.")
    except Exception as e:  # noqa: BLE001
        print(f"   ⚠️ فشل إرسال البريد ({e})، الصفقة نفسها نجحت رغم ذلك.")
