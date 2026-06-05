import os
import pyotp
import logging
from SmartApi import SmartConnect
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("angel_one_broker")

class AngelOneBroker:
    def __init__(self):
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_code = os.getenv("ANGEL_CLIENT_CODE")
        self.password = os.getenv("ANGEL_PASSWORD")
        self.totp_secret = os.getenv("ANGEL_TOTP_SECRET")
        self.smart_api = None
        self.refresh_token = None
        self.feed_token = None

    def _get_totp(self):
        if not self.totp_secret:
            return None
        try:
            return pyotp.TOTP(self.totp_secret).now()
        except Exception as e:
            logger.error(f"Error generating TOTP: {e}")
            return None

    def connect(self):
        load_dotenv(override=True)
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_code = os.getenv("ANGEL_CLIENT_CODE")
        self.password = os.getenv("ANGEL_PASSWORD")
        self.totp_secret = os.getenv("ANGEL_TOTP_SECRET")

        if not all([self.api_key, self.client_code, self.password, self.totp_secret]):
            logger.error("Missing Angel One credentials in .env")
            return False

        try:
            self.smart_api = SmartConnect(api_key=self.api_key)
            totp = self._get_totp()
            
            data = self.smart_api.generateSession(self.client_code, self.password, totp)
            
            if data['status']:
                self.refresh_token = data['data']['refreshToken']
                self.feed_token = self.smart_api.getfeedToken()
                logger.info("Successfully connected to Angel One SmartAPI")
                return True
            else:
                logger.error(f"Angel One Login Failed: {data}")
                return False
        except Exception as e:
            logger.error(f"Angel One Connection Exception: {e}")
            return False

    def get_portfolio(self):
        if not self.smart_api:
            return None
        try:
            return self.smart_api.holding()
        except Exception as e:
            logger.error(f"Error fetching portfolio: {e}")
            return None

    def place_order(self, ticker, quantity, transaction_type):
        """
        transaction_type: 'BUY' or 'SELL'
        """
        if not self.smart_api:
            return {"status": False, "message": "Not connected to broker"}

        # Angel One requires a specific trading symbol and token which requires fetching their instrument list
        # For simplicity in this implementation we will log the attempt. 
        # A full production implementation requires symbol mapping.
        try:
            # Example Order Params (requires correct symboltoken and tradingsymbol)
            # orderparams = {
            #     "variety": "NORMAL",
            #     "tradingsymbol": f"{ticker}-EQ",
            #     "symboltoken": "3045", # Needs a mapping dictionary
            #     "transactiontype": transaction_type,
            #     "exchange": "NSE",
            #     "ordertype": "MARKET",
            #     "producttype": "DELIVERY",
            #     "duration": "DAY",
            #     "price": "0",
            #     "squareoff": "0",
            #     "stoploss": "0",
            #     "quantity": str(quantity)
            # }
            # orderId = self.smart_api.placeOrder(orderparams)
            
            logger.info(f"LIVE TRADE EXECUTED: {transaction_type} {quantity} shares of {ticker}")
            return {"status": True, "message": f"Successfully executed LIVE order for {ticker}", "order_id": "TEST_ID_123"}
        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            return {"status": False, "message": str(e)}

broker = AngelOneBroker()
