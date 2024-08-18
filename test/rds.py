# package import statement
from SmartApi.smartConnect import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import time
import pyotp
from logzero import logger

api_key = '7KRaMCsN'
username = 'D52721094'
pwd = '4400'
smart_connect = SmartConnect(api_key)
try:
    token = "NHSTELYG24CVPPWEDS2ABGDU4M"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
data = smart_connect.generateSession(username, pwd, totp)

if data['status'] == False:
    logger.error(data)
    
else:
    # login api call
    # logger.info(f"You Credentials: {data}")
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    # fetch the feedtoken
    feedToken = smart_connect.getfeedToken()
    # fetch User Profile
    res = smart_connect.getProfile(refreshToken)
    smart_connect.generateToken(refreshToken)
    res=res['data']['exchanges']

# Function to get the symbol token for the option
def get_symbol_token(symbol):
    try:
        # Here, you would normally retrieve or generate the token; placeholder for now
        symbol_token = "symbol_token_placeholder"
        logger.info(f"Symbol token for {symbol} is {symbol_token}")
        return symbol_token
    except Exception as e:
        logger.error(f"Failed to get symbol token for {symbol}: {str(e)}")
        return None

def get_option_ltp(symbol, exchange, symbol_token):
    try:
        ltp_data = smart_connect.ltpData(exchange, symbol_token, symbol)
        if ltp_data and ltp_data['status']:
            ltp = ltp_data['data']['ltp']
            logger.info(f"LTP for {symbol} is {ltp}")
            return ltp
        else:
            logger.error(f"Failed to get LTP for {symbol}. Response: {ltp_data}")
            return None
    except Exception as e:
        logger.error(f"Failed to get LTP for {symbol}: {str(e)}")
        if "exceeding access rate" in str(e):
            logger.error("Rate limit exceeded. Sleeping for 60 seconds.")
            time.sleep(60)  # Sleep for 60 seconds to allow the rate limit to reset
        return None


# Function to auto-select the strike price based on the premium range
def auto_select_strike(exchange, option_type, expiry, premium_range):
    # Define a range of strike prices to check
    strike_price_range = range(48000, 53000, 100)
    
    for strike_price in strike_price_range:
        symbol = f"BANKNIFTY{expiry}{strike_price}{option_type}"
        symbol_token = get_symbol_token(symbol)
        if not symbol_token:
            logger.error(f"Invalid symbol token for {symbol}")
            continue
        
        ltp = get_option_ltp(symbol, exchange, symbol_token)
        if ltp and premium_range[0] <= ltp <= premium_range[1]:
            logger.info(f"Selected strike price {symbol} with premium {ltp}")
            return symbol, symbol_token
        elif ltp is None:
            logger.error(f"Skipping {symbol} due to LTP retrieval failure.")
            continue

    logger.info(f"No strikes found within premium range {premium_range}")
    return None, None

# Function to place an order
def place_order(symbol, exchange, transaction_type, quantity, symbol_token, price=None, order_type="MARKET"):
    try:
        order_params = {
            "variety": "NORMAL",  # NORMAL for intraday
            "tradingsymbol": symbol,
            "symboltoken": symbol_token,
            "exchange": exchange,
            "transactiontype": transaction_type,  # "BUY" or "SELL"
            "ordertype": order_type,  # "MARKET" or "LIMIT"
            "producttype": "INTRADAY",  # Product type
            "duration": "DAY",  # Duration of the order
            "price": price if price else 0,  # Price for LIMIT order
            "squareoff": "0",  # Square off
            "stoploss": "0",  # Stop loss
            "quantity": quantity  # Quantity to trade
        }

        # Place the order
        order_id = smart_connect.placeOrder(order_params)
        logger.info(f"Order placed successfully: Order ID = {order_id}")
        return order_id

    except Exception as e:
        logger.error(f"Order placement failed: {str(e)}")
        return None

# Example usage: Placing an order only if a strike price with premium within the specified range is found
def execute_trade():
    symbol = "BANKNIFTY"
    exchange = "NSE_FO"
    option_type = "CE"  # Call Option
    expiry = "21AUG"  # Example expiry date
    transaction_type = "BUY"
    quantity = 15  # Lot size for BankNifty options
    premium_range = (450, 550)  # Desired premium range

    symbol, symbol_token = auto_select_strike(exchange, option_type, expiry, premium_range)
    if not symbol:
        logger.error("No suitable strike price found. Trade not executed.")
        return

    order_id = place_order(symbol, exchange, transaction_type, quantity, symbol_token)
    if order_id:
        logger.info(f"Trade executed successfully: Order ID = {order_id}")
    else:
        logger.error("Trade execution failed.")

# Execute the trade
execute_trade()