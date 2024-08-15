# package import statement
from SmartApi import SmartConnect #or from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger

api_key = '7KRaMCsN'
username = 'D52721094'
pwd = '4400'
smartApi = SmartConnect(api_key)
try:
    token = "NHSTELYG24CVPPWEDS2ABGDU4M"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
data = smartApi.generateSession(username, pwd, totp)

if data['status'] == False:
    logger.error(data)
    
else:
    # login api call
    # logger.info(f"You Credentials: {data}")
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    # fetch the feedtoken
    feedToken = smartApi.getfeedToken()
    # fetch User Profile
    res = smartApi.getProfile(refreshToken)
    smartApi.generateToken(refreshToken)
    res=res['data']['exchanges']

   # Function to get the symbol token for the option
def get_symbol_token(symbol):
    try:
        search_result = SmartConnect.searchSymbol('NFO', symbol)
        if search_result and len(search_result['data']) > 0:
            symbol_token = search_result['data'][0]['token']
            logger.info(f"Symbol token for {symbol} is {symbol_token}")
            return symbol_token
        else:
            logger.error(f"Symbol token not found for {symbol}")
            return None
    except Exception as e:
        logger.error(f"Failed to get symbol token for {symbol}: {str(e)}")
        return None

# Function to get the LTP (Last Traded Price) of an option
def get_option_ltp(symbol, exchange, symbol_token):
    try:
        ltp_data = SmartConnect.ltpData(exchange, symbol_token, symbol)
        ltp = ltp_data['data']['ltp']
        logger.info(f"LTP for {symbol} is {ltp}")
        return ltp
    except Exception as e:
        logger.error(f"Failed to get LTP for {symbol}: {str(e)}")
        return None

# Function to place an order
def place_order(symbol, exchange, transaction_type, quantity, price=None, order_type="MARKET"):
    try:
        symbol_token = get_symbol_token(symbol)
        if not symbol_token:
            return None

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
        order_id = SmartConnect.placeOrder(order_params)
        logger.info(f"Order placed successfully: Order ID = {order_id}")
        return order_id

    except Exception as e:
        logger.error(f"Order placement failed: {str(e)}")
        return None

# Example usage: Placing an order only if the premium is within the specified range
def execute_trade():
    symbol = "BANKNIFTY24AUG24000CE"  # Replace with the correct option symbol
    exchange = "NFO"
    transaction_type = "BUY"
    quantity = 75  # Lot size for BankNifty options
    premium_range = (450, 550)  # Desired premium range

    symbol_token = get_symbol_token(symbol)
    if not symbol_token:
        logger.error("Symbol token retrieval failed. Trade not executed.")
        return

    ltp = get_option_ltp(symbol, exchange, symbol_token)
    if ltp and premium_range[0] <= ltp <= premium_range[1]:
        logger.info(f"Premium is within range: {ltp}. Proceeding with trade.")
        order_id = place_order(symbol, exchange, transaction_type, quantity)
        if order_id:
            logger.info(f"Trade executed successfully: Order ID = {order_id}")
        else:
            logger.error("Trade execution failed.")
    else:
        logger.info(f"Premium {ltp} is out of range. Trade not executed.")

# Execute the trade
execute_trade()