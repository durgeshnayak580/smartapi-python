# package import statement
from SmartApi.smartConnect import SmartConnect #or from SmartApi.smartConnect import SmartConnect
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

# place order
try:
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "BANKNIFTY",
        "symboltoken": "BANKNIFTY21AUG50500CE",
        "transactiontype": "BUY",
        "exchange": "NSE_FO",
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "optiontype": "CE",
        "expiry": "21AUG",
        "duration": "DAY",
        "squareoff": 0,
        "stoploss": 0,
        "quantity": 3
    }

    # Method 1: Place an order and return the order ID
    orderid = smartApi.placeOrder(orderparams)
    logger.info(f"PlaceOrder : {orderid}")
    # Method 2: Place an order and return the full response
    response = smartApi.placeOrderFullResponse(orderparams)
    logger.info(f"PlaceOrder : {response}")
except Exception as e:
    logger.exception(f"Order placement failed: {e}")

