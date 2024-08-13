
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
