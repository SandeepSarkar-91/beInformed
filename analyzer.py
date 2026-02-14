import re
from transcripts import ScreenerScraper

class TradingAnalyzer:
    def __init__(self, parser):
        self.parser = parser
        self.scraper = ScreenerScraper()

    def get_market_state(self, current_nifty_change):
        """
        Logic to determine market state:
        - Down: < -0.5%
        - Up: > 0.5%
        - Flat: between -0.5% and 0.5%
        """
        if current_nifty_change < -0.005:
            return "DOWN"
        elif current_nifty_change > 0.005:
            return "UP"
        else:
            return "FLAT"

    def is_price_below_200dma(self, symbol, current_price, dma_200):
        """
        Rule: Only trade if current price < 200 DMA.
        Exempting Gold/Silver ETFs from this rule as per instructions.
        """
        gold_silver_keywords = ["GOLD", "SILVE", "GOLDBEES"]
        if any(kd in symbol.upper() for kd in gold_silver_keywords):
            return True, "Exempt from DMA rule (Gold/Silver)"
            
        if current_price < dma_200:
            return True, f"Price {current_price} is below 200 DMA {dma_200}"
        else:
            return False, f"Price {current_price} is NOT below 200 DMA {dma_200}"

    def confirm_with_qualitative_data(self, symbol):
        """
        Fetches announcements from Screener.in and performs a basic check
        for significant positive or negative news.
        """
        data = self.scraper.get_company_data(symbol)
        if not data:
            return True, "No qualitative data found, proceeding with technical check."
        
        announcements = data.get("announcements", [])
        concalls = data.get("concall_summaries", [])
        
        # Simple keyword matching for demo; in production, this would be an LLM call
        negative_keywords = ["loss", "penalty", "default", "resignation", "investigation"]
        positive_keywords = ["order", "growth", "expansion", "profit", "dividend", "bonus"]
        
        for ann in announcements:
            text = ann['text'].lower()
            if any(k in text for k in negative_keywords):
                return False, f"Vetoed: Negative announcement found: {ann['text']}"
            
        return True, f"Qualitative check passed. Found {len(announcements)} announcements."

    def suggest_trades(self, market_state):
        # Specific symbols extracted from user screenshots
        WATCHLIST = {
            "FLAT": ["SETFGLD", "ZGOLD", "SILVERBEES", "ITC", "HCLTECH", "CAMS", "CIPLA", "BALKRISHNA"],
            "DOWN": ["NASDQ100", "NASDQ50", "NYFANG", "CDSL", "BSE", "MCX", "HAL", "BEL", "JIOFIN", "KFINTECH", "NAUKRI", "DIVISLAB", "WAAREEENER", "WAAREERTI", "HINDCOPPER", "ANANTRAJ"],
            "UP": ["SETFGLD", "ZGOLD", "SILVERBEES"]
        }
        
        # Mapped common names to likely NSE symbols (Approximated)
        SYMBOLS = {
            "FLAT": ["SETFGLD", "ZGOLD", "SILVERBEES", "ITC", "HCLTECH", "CAMS", "CIPLA", "BALKRISIND"],
            "DOWN": ["MON100", "MONQ50", "MAFANG", "CDSL", "BSE", "MCX", "HAL", "BEL", "JIOFIN", "KFINTECH", "NAUKRI", "DIVISLAB", "WAAREEENER", "WAAREERTI", "HINDCOPPER", "ANANTRAJ"],
            "UP": ["SETFGLD", "ZGOLD", "KOTAKSILVE"]
        }

        if market_state == "FLAT":
            return {
                "assets": SYMBOLS["FLAT"],
                "reasoning": "Market is flat. Strategy: Gold/Silver ETFs and Dividend/Quality stocks from watchlist."
            }
        elif market_state == "DOWN":
            return {
                "assets": SYMBOLS["DOWN"],
                "reasoning": "Market is down. Strategy: Index ETFs and Monopoly/Growth businesses from watchlist."
            }
        elif market_state == "UP":
            return {
                "assets": SYMBOLS["UP"],
                "reasoning": "Market is up. Strategy: Gold/Silver ETFs only as per philosophy."
            }
        
        return {"assets": [], "reasoning": "No specific strategy for this state."}
