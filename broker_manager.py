import os
import pandas as pd
from abc import ABC, abstractmethod

class Broker(ABC):
    @abstractmethod
    def get_balance(self):
        pass

    @abstractmethod
    def place_order(self, symbol, quantity, side, order_type, price=None):
        pass

    @abstractmethod
    def get_positions(self):
        pass

class HDFCSkyBroker(Broker):
    def __init__(self, api_key, api_secret, session_token=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session_token = session_token
        self.base_url = "https://api.hdfcsec.com/individual" # Example base URL from docs
        print("HDFC Sky Broker initialized. Ready for API keys.")

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key,
            "Authorization": f"Bearer {self.session_token}"
        }

    def get_balance(self):
        # In production: response = requests.get(f"{self.base_url}/funds", headers=self._get_headers())
        return 10000.0

    def place_order(self, symbol, quantity, side, order_type, price=None):
        """
        Implementation based on HDFC InvestRight API docs
        """
        payload = {
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "order_type": order_type,
            "price": price if price else 0,
            "exchange": "NSE"
        }
        print(f"DEBUG: Calling HDFC Sky API to {side} {symbol}")
        # In production: response = requests.post(f"{self.base_url}/orders", json=payload, headers=self._get_headers())
        return {"status": "success", "order_id": "MOCK_HDFC_123"}

    def get_positions(self):
        # In production: response = requests.get(f"{self.base_url}/positions", headers=self._get_headers())
        return []

class SafetyManager:
    def __init__(self, total_capital=10000.0, max_daily_loss=500.0):
        self.total_capital = total_capital
        self.max_daily_loss = max_daily_loss
        self.current_loss = 0.0

    def check_trade_safety(self, position_size_value):
        if position_size_value > self.total_capital:
            return False, f"Position size {position_size_value} exceeds total capital {self.total_capital}"
        
        if self.current_loss >= self.max_daily_loss:
            return False, f"Daily loss limit {self.max_daily_loss} reached"
            
        return True, "Safe"

    def update_loss(self, daily_pnl):
        self.current_loss = abs(min(0, daily_pnl))
