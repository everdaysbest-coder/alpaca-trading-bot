"""
config.py
=========
إعدادات المخاطرة الأساسية وقائمة الأسهم المستهدفة.
كل هذه القيم قابلة للتعديل، لكنها مصمّمة افتراضيًا لمخاطرة منخفضة.
"""

import os

ALPACA_API_KEY = os.environ["ALPACA_API_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]
ALPACA_BASE_URL = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
ALPACA_DATA_URL = "https://data.alpaca.markets"

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL_FALLBACKS = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-pro-latest"]

# أسهم كبيرة وسائلة من قطاعات متنوعة (تقنية، طاقة، صحة، استهلاك، صناعة، تمويل)
# التنويع بين القطاعات يرفع احتمال ظهور توافق بين الإشارة الفنية والأخبار في أي وقت،
# لأن قطاعات مختلفة تتحرك بدورات وأوقات مختلفة
WATCHLIST = [
    # تقنية
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META",
    # سيارات وطاقة
    "TSLA", "XOM", "CVX",
    # تمويل
    "JPM", "V", "MA",
    # صحة
    "JNJ", "UNH", "PFE",
    # استهلاك وتجزئة
    "WMT", "KO", "MCD",
    # صناعة
    "CAT", "BA",
    # صناديق مؤشرات واسعة (تنويع إضافي داخل الصفقة الواحدة)
    "SPY", "QQQ",
]

# --- إدارة المخاطرة ---
MAX_POSITION_PCT = 0.05        # أقصى 5% من رأس المال المتاح لكل صفقة
STOP_LOSS_PCT = 0.02           # وقف خسارة تلقائي عند -2%
TAKE_PROFIT_PCT = 0.04         # جني أرباح تلقائي عند +4% (مخاطرة:عائد = 1:2)
MAX_OPEN_POSITIONS = 5         # أقصى عدد صفقات مفتوحة في نفس الوقت
DAILY_LOSS_LIMIT_PCT = 0.03    # قاطع دائرة: توقف عن الشراء لو خسر الحساب 3% في نفس اليوم

# --- الإشارة الفنية ---
SHORT_MA_PERIOD = 5
LONG_MA_PERIOD = 20

