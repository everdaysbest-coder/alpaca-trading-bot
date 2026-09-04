"""
analysis.py
===========
إشارتان بسيطتان وشفافتان يجب أن تتوافقا معًا قبل أي قرار شراء:
1. إشارة فنية: تقاطع متوسط متحرك قصير فوق متوسط طويل (زخم صاعد)
2. إشارة أخبار: تصنيف مزاج آخر العناوين عبر Gemini (إيجابي/محايد/سلبي)
"""

import json
import time

import requests

from config import GEMINI_API_KEY, GEMINI_MODEL_FALLBACKS, SHORT_MA_PERIOD, LONG_MA_PERIOD


def moving_average(prices: list, period: int) -> float | None:
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def technical_signal(prices: list) -> str:
    """يرجع 'bullish' لو المتوسط القصير فوق الطويل، وإلا 'neutral'."""
    short_ma = moving_average(prices, SHORT_MA_PERIOD)
    long_ma = moving_average(prices, LONG_MA_PERIOD)
    if short_ma is None or long_ma is None:
        return "neutral"  # بيانات غير كافية بعد
    return "bullish" if short_ma > long_ma else "neutral"


def news_sentiment(symbol: str, headlines: list, retries: int = 3) -> str:
    """يرجع 'positive' أو 'neutral' أو 'negative' بناءً على تحليل Gemini للعناوين."""
    if not headlines:
        return "neutral"  # لا أخبار = لا إشارة سلبية، لكن أيضًا لا دافع قوي

    prompt = f"""Analyze the overall sentiment of these recent news headlines about the stock {symbol}
for a conservative, risk-averse trading system. Headlines:
{chr(10).join(f"- {h}" for h in headlines)}

Return STRICTLY valid JSON, no markdown fences:
{{"sentiment": "positive" | "neutral" | "negative", "reason": "one short sentence"}}"""

    last_error = None
    for attempt in range(retries + 1):
        model = GEMINI_MODEL_FALLBACKS[attempt % len(GEMINI_MODEL_FALLBACKS)]
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"},
                },
                timeout=30,
            )
            if r.status_code in (429, 503) and attempt < retries:
                time.sleep(15 * (attempt + 1))
                continue
            r.raise_for_status()
            data = r.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(text)
            return result.get("sentiment", "neutral")
        except Exception as e:  # noqa: BLE001
            last_error = e
            if attempt < retries:
                time.sleep(15 * (attempt + 1))

    print(f"   ⚠️ تعذّر تحليل الأخبار لـ {symbol} ({last_error})، اعتُبرت محايدة احتياطًا.")
    return "neutral"


def should_buy(prices: list, symbol: str, headlines: list) -> tuple[bool, str]:
    """القرار النهائي: شراء فقط لو الإشارتان متوافقتان (فني صاعد + أخبار ليست سلبية)."""
    tech = technical_signal(prices)
    sentiment = news_sentiment(symbol, headlines)

    if tech == "bullish" and sentiment != "negative":
        return True, f"فني: {tech}, أخبار: {sentiment}"
    return False, f"فني: {tech}, أخبار: {sentiment}"
