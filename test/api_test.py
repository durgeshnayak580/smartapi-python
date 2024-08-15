from SmartApi.smartConnect import SmartConnect
import pyotp
import time as time
from datetime import time, datetime, timedelta
import json

# Angel One API credentials
API_KEY = "7KRaMCsN"
CLIENT_ID = "D52721094"
PASSWORD = "4400"
TOTP_SECRET = 'NHSTELYG24CVPPWEDS2ABGDU4M'
SYMBOL_TOKEN = '26009'  # Bank Nifty CE/PE Symbol token for options

# Set trading parameters
CAPITAL = 60000
LOT_SIZE = 15
EXPIRY = 'current_week'
PREMIUM_RANGE = (450, 550)
PROFIT_TARGET = 1.25  # 25% Profit Target
STOP_LOSS_TRAIL = 0.1  # 10% Trailing Stop Loss
MAX_TRADES = 2
AUTO_SQUARE_OFF = time(15, 15)
NO_ENTRY_AFTER = time(14, 0)

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
        "tradingsymbol": symbol_token,
        "symboltoken": 26009,
        "transactiontype": transaction_type,
        "exchange": "NSE",
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "optiontype": "CE",
        "duration": "DAY",
        "price": price,
        "squareoff": 0,
        "stoploss": 0,
        "quantity": quantity,
    }
    order_response = smart_connect.placeOrder(order_params)
    return order_response

# Function to fetch historical data
def fetch_historical_data(symbol_token, interval='FIVE_MINUTE'):
    from_time = datetime.now() - timedelta(days=1)
    to_time = datetime.now()
    historical_params = {
        "exchange": "NSE",
        "symboltoken": symbol_token,
        "interval": FIVE_MINUTE,
        "fromdate": from_time.strftime('%Y-%m-%d %H:%M'),
        "todate": to_time.strftime('%Y-%m-%d %H:%M'),
    }
    data = smart_connect.getCandleData(historical_params)
    df = getattr.DataFrame(data['data'])
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

def fetch_order_book():
    try:
        response = smart_connect.getOrderBook()
        if response['status']:
            return json.dumps(response['data'])
        else:
            print(f"Error fetching order book: {response['message']}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching order book: {e}")
        return None

def check_open_trades():
    order_book_response = fetch_order_book()  # Get the order book data
    if order_book_response:
        order_book = json.loads(order_book_response)  # Parse the JSON response
        open_trades = [order for order in order_book if order['status'] in ['open', 'trigger pending']]
        return len(open_trades) > 0
    else:
        return False

def bullish_engulfing_strategy(trades_today):
    if check_open_trades():
        print("There are open trades, no new trades will be placed.")
    else:
        print("No open trades, proceed with placing a new trade.")
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
            time(0, 5)  # Wait for 5 minutes before checking again
run_strategy()
