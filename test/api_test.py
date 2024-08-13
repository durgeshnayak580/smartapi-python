from smartapi import SmartConnect
import pyotp
import pandas as pd
import time as time
from datetime import datetime, timedelta

# Angel One API credentials
API_KEY = 'EUGl8dR1'
CLIENT_ID = 'D52721094'
PASSWORD = 'Dn3371dyi12'
TOTP_SECRET = 'NHSTELYG24CVPPWEDS2ABGDU4M'
SYMBOL_TOKEN = '99926009'  # Bank Nifty CE/PE Symbol token for options

# Set trading parameters
CAPITAL = 60000
LOT_SIZE = 15
EXPIRY = 'current_week'
PREMIUM_RANGE = (450, 550)
PROFIT_TARGET = 1.25  # 25% Profit Target
STOP_LOSS_TRAIL = 0.1  # 10% Trailing Stop Loss
MAX_TRADES = 2
NO_ENTRY_AFTER = time(14, 0)
AUTO_SQUARE_OFF = time(15, 15)

# Connect to Angel One SmartAPI
smart_connect = SmartConnect(api_key=API_KEY)
totp_code = pyotp.TOTP(TOTP_SECRET).now()
session = smart_connect.generateSession(CLIENT_ID, PASSWORD, totp_code)

# Set headers for authenticated requests
auth_token = session['data']['jwtToken']
refresh_token = session['data']['refreshToken']
feed_token = smart_connect.getfeedToken()

# Function to place an order
def place_order(transaction_type, quantity, price, symbol_token):
    order_params = {
        "variety": "NORMAL",
        "tradingsymbol": 99926009,
        "symboltoken": 99926009,
        "transactiontype": transaction_type,
        "exchange": "NFO",
        "ordertype": "market_price",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": price,
        "squareoff": 0,
        "stoploss": 0,
        "quantity": 3,
    }
    order_response = smart_connect.placeOrder(order_params)
    return order_response

# Function to fetch historical data
def fetch_historical_data(symbol_token, interval='FIVE_MINUTE'):
    from_time = datetime.now() - timedelta(days=1)
    to_time = datetime.now()
    historical_params = {
        "exchange": "NFO",
        "symboltoken": 99926009,
        "interval": interval,
        "fromdate": from_time.strftime('%Y-%m-%d %H:%M'),
        "todate": to_time.strftime('%Y-%m-%d %H:%M'),
    }
    data = smart_connect.getCandleData(historical_params)
    df = pd.DataFrame(data['data'])
    return df

# Function to implement trailing stop loss
def trailing_stop_loss(entry_price, current_price, stop_loss, trail_percentage=0.10):
    trail_stop = entry_price * (1 + trail_percentage / 100)
    if current_price >= trail_stop:
        return max(stop_loss, trail_stop)
    return stop_loss

# Function to log trade details
def log_trade(entry_date, entry_time, exit_date, exit_time, profit_loss):
    with open('trade_log.csv', 'a') as file:
        file.write(f"{entry_date},{entry_time},{exit_date},{exit_time},{profit_loss}\n")

# Function to check for open trades
def check_open_trades():
    order_book = smart_connect.orderBook()
    open_trades = [order for order in order_book if order['status'] in ['open', 'trigger pending']]
    return len(open_trades) > 0

# Function to execute the strategy
def bullish_engulfing_strategy(trades_today):
    if check_open_trades():
        print("Open trades detected, skipping new order.")
        return trades_today
    
data = fetch_historical_data(SYMBOL_TOKEN)
    
if len(data) < 2:
    return trades_today
    
    last_candle = data.iloc[-1]
    previous_candle = data.iloc[-2]
    
# Check for Bullish Engulfing Pattern
    if previous_candle['close'] < previous_candle['open'] and \
       last_candle['close'] > last_candle['open'] and \
       last_candle['high'] > previous_candle['high'] and \
       last_candle['close'] > previous_candle['high']:
        
# Check if price is within premium range
    price = last_candle['close']
    if PREMIUM_RANGE[0] <= price <= PREMIUM_RANGE[1]:
       quantity = 3 * LOT_SIZE  # 3 lots of 15 each
       order_response = place_order('BUY', quantity, price, SYMBOL_TOKEN)
       print('Order Response:', order_response)
       trades_today += 1
            
# Implement profit target and stop loss
       entry_price = price
       stop_loss = previous_candle['low']
       target_price = entry_price * PROFIT_TARGET
            
       entry_date = datetime.now().date()
       entry_time = datetime.now().time()
            
while True:
       current_data = fetch_historical_data(SYMBOL_TOKEN).iloc[-1]
       current_price = current_data['close']
                
if current_price <= stop_loss:
       place_order('SELL', quantity, current_price, SYMBOL_TOKEN)
       print('Stop loss hit. Exiting position.')
       profit_loss = (current_price - entry_price) * quantity
       exit_date = datetime.now().date()
       exit_time = datetime.now().time()
       log_trade(entry_date, entry_time, exit_date, exit_time, profit_loss)
       break
elif current_price >= target_price:
       place_order('SELL', quantity, current_price, SYMBOL_TOKEN)
       print('Target hit. Exiting position.')
       profit_loss = (current_price - entry_price) * quantity
       exit_date = datetime.now().date()
       exit_time = datetime.now().time()
       log_trade(entry_date, entry_time, exit_date, exit_time, profit_loss)
       break
                
# Update trailing stop loss
       stop_loss = trailing_stop_loss(entry_price, current_price, stop_loss, STOP_LOSS_TRAIL)
else:
      print('No Bullish Engulfing Pattern detected.')
    
    return trades_today

# Main function to run the strategy
def run_strategy():
    trades_today = 0
    while True:
        now = datetime.now()
        current_time = now.time()
        if now.weekday() < 5 and time(9, 15) <= current_time <= AUTO_SQUARE_OFF:
            if current_time < NO_ENTRY_AFTER and trades_today < MAX_TRADES:
                trades_today = bullish_engulfing_strategy(trades_today)
            else:
                print('Maximum trades reached or past entry time. No more trades today.')
                break
        else:
            print('Outside trading hours. Waiting...')
        time.sleep(300)  # Wait for 5 minutes before checking again
       
       # Placeholder list for open trades
open_trades = []

def close_all_open_trades():
    print("Closing all open trades...")
    for trade in open_trades:
        # Assuming trade.close() is the method to close a trade
        trade.close()
    open_trades.clear()  # Clear the list after closing all trades
    print("All open trades closed.")

def main_trading_logic():
    try:
        # Example of fetching live data
        start_time = time.time()
        fetch_data()
        elapsed_time = time.time() - start_time

        if elapsed_time > 30:
            print("Data fetch took more than 30 seconds, engine off.")
            close_all_open_trades()
            return

        # Example of handling broker error
        if broker_error_detected():
            print("Broker error detected, engine off.")
            close_all_open_trades()
            return

        # Rest of your trading logic

    except Exception as e:
        print(f"Error occurred: {e}")
        close_all_open_trades()

def fetch_data():
    # Simulate data fetching
    time.sleep(1)  # Simulate a delay

def broker_error_detected():
    # Placeholder for detecting broker errors
    return False

# Example trade object and method to simulate placing a trade
class Trade:
    def __init__(self, trade_id):
        self.trade_id = trade_id
    
    def close(self):
        print(f"Trade {self.trade_id} closed.")

# Simulate placing trades
open_trades.append(Trade(1))
open_trades.append(Trade(2))

run_strategy()
    # # Websocket Programming

    from SmartApi.smartWebSocketV2 import SmartWebSocketV2

    AUTH_TOKEN = authToken
    API_KEY = api_key
    CLIENT_CODE = username
    FEED_TOKEN = feedToken
    # correlation_id = "abc123"
    action = 1
    mode = 1

    token_list = [
        {
            "exchangeType": 1,
            "tokens": ["26009","1594"]
        }
    ]
    token_list1 = [
        {
            "action": 0,
            "exchangeType": 1,
            "tokens": ["26009"]
        }
    ]

    #retry_strategy=0 for simple retry mechanism
    sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN,max_retry_attempt=2, retry_strategy=0, retry_delay=10, retry_duration=30)

    #retry_strategy=1 for exponential retry mechanism
    # sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN,max_retry_attempt=3, retry_strategy=1, retry_delay=10,retry_multiplier=2, retry_duration=30)

    def on_data(wsapp, message):
        logger.info("Ticks: {}".format(message))
        close_connection()

    def on_control_message(wsapp, message):
        logger.info(f"Control Message: {message}")

    def on_open(wsapp):
        logger.info("on open")
        some_error_condition = False
        if some_error_condition:
            error_message = "Simulated error"
            if hasattr(wsapp, 'on_error'):
                wsapp.on_error("Custom Error Type", error_message)
        else:
            sws.subscribe(correlation_id, mode, token_list)
            # sws.unsubscribe(correlation_id, mode, token_list1)

    def on_error(wsapp, error):
        logger.error(error)

    def on_close(wsapp):
        logger.info("Close")

    def close_connection():
        sws.close_connection()


    # Assign the callbacks.
    sws.on_open = on_open
    sws.on_data = on_data
    sws.on_error = on_error
    sws.on_close = on_close
    sws.on_control_message = on_control_message

    sws.connect()


    ########################### SmartWebSocket OrderUpdate Sample Code Start Here ###########################
    from SmartApi.smartWebSocketOrderUpdate import SmartWebSocketOrderUpdate
    client = SmartWebSocketOrderUpdate(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
    client.connect()
    ########################### SmartWebSocket OrderUpdate Sample Code End Here ###########################
