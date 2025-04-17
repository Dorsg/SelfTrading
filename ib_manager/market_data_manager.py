from datetime import datetime
import os
import time
import pandas_market_calendars as mcal
import finnhub
import logging

from dotenv import load_dotenv
import pytz
logger = logging.getLogger(__name__)

load_dotenv()

FINNHUB = os.getenv("FINNHUB_API_KEY")


class MarketDataManager:
    def __init__(self, api_key=None):
        self.api_key = api_key or FINNHUB
        self.client = finnhub.Client(api_key=self.api_key)

    def get_current_price(self, symbol: str):
        """
        Fetches the current real-time price for a stock symbol.
        """
        try:
            quote = self.client.quote(symbol)
            price = quote.get('c')  # 'c' = current price
            if price:
                logger.info("Fetched real-time price for %s: %.2f", symbol, price)
                return round(price, 2)
            else:
                logger.warning("No current price found for %s", symbol)
                return None
        except Exception:
            logger.exception("Failed to get current price for %s", symbol)
            return None

    def get_historical_candles(self, symbol: str, resolution: str = '5', count: int = 100):
        """
        Fetch historical candles for a symbol.
        Resolution: '1', '5', '15', '30', '60', 'D', 'W', 'M'
        Count: number of candles
        """
        try:
            now = int(time.time())
            delta = count * 60 * int(resolution) if resolution.isdigit() else count * 24 * 60 * 60
            start = now - delta
            candles = self.client.stock_candles(symbol, resolution, start, now)

            if candles.get("s") == "ok":
                logger.info("Fetched %d candles for %s [%s min]", len(candles['c']), symbol, resolution)
                return candles
            else:
                logger.warning("No candle data returned for %s", symbol)
                return None
        except Exception:
            logger.exception("Failed to get candle data for %s", symbol)
            return None
        
    def is_market_open(self) -> bool:
        """
        True  → US equities can trade *right now* (pre, regular, or after‑hours).
        False → fully closed (weekend or between 20:00‑04:00 ET or holiday).
        No external HTTP; relies on NYSE calendar + local clock.
        """
        eastern = pytz.timezone("US/Eastern")
        now_et  = datetime.now(eastern)

        # NYSE calendar gives you the *regular* session for today
        nyse = mcal.get_calendar('NYSE')
        sched = nyse.schedule(start_date=now_et.date(), end_date=now_et.date())
        if sched.empty:              # weekend or exchange holiday
            return False

        reg_open  = sched.iloc[0]['market_open'].tz_convert(eastern)
        reg_close = sched.iloc[0]['market_close'].tz_convert(eastern)

        # Extended hours window 04:00‑20:00 ET
        ext_open  = reg_open.replace(hour=4,  minute=0)
        ext_close = reg_close.replace(hour=20, minute=0)

        return ext_open <= now_et <= ext_close