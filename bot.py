import datetime



##TODO init a DatabaseInteraction() object titled mysql_connector for use in other objects
##TODO init an IBApi() object titled ibapi_client
##TODO init a threading_manager() object titled threading_manager for use in other objects
##TODO init a realtimedata() object titled realtime_data_manager for use in other objects
##TODO init a HistoricalDataManager() object titled historical_data_manager for use in other objects
##TODO init a TechnicalAnalysisProcessor() object titled ta_manager for use in other objects
##TODO solve how to handle the bar class object

class Bar:
    first_historical_bar = True
    def __init__(self, open_, high, low, close, volume, date, tick):
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        if Bar.first_historical_bar:
            self.date = datetime.now()
            Bar.first_historical_bar = False
        else:
            self.date = date
        self.tick = tick

class Bot:
    ib = None
    bar_size = 1
    currentBar = None
    df_dict = {}  # Dictionary to store DataFrames for each symbol
    reqID = 1
    global orderId
    symbols = ["ENEL", "ENI", "ISP", "UCG", "G", "PIRC", "SPM", "UNI", "BAMI", "LDO"]
    initial_bar_time = datetime.now().astimezone(pytz.timezone("Europe/Berlin"))
    sym_dict = {} # stores a symbol, reqID pair
    mysql_engine = None  # Declare mysql_engine as a class variable

    # what is automatically run when an instance of the class is created
    def __init__(self):

        # Connect to IB on init & Pass the realtime_buffer when creating an instance of IBApi
        self.ib = IBApi(self)
        self.ib.connect("127.0.0.1", 7497, 1)
        print("Connected to Interactive Brokers")

        # Start a separate thread for IB communication
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)

        self.threading_attributes_by_symbol = {}  # stores buffer, lock, flags for symbol specific threads

        # Initialize currentBar with default values
        self.currentBar = Bar(open_=0, high=0, low=0, close=0, volume=0,
                              date=datetime.now().astimezone(pytz.timezone("Europe/Berlin")),
                              tick=datetime.now().astimezone(pytz.timezone("Europe/Berlin")))
        # print("Initial currentBar data:", vars(self.currentBar))  # Print data after bar creation

        # For each symbol, initialize a DataFrame with necessary columns
        for symbol in self.symbols:  # iterate over class variable 'symbols'
            self.df_dict[symbol] = pandas.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Date', 'Tick',
                                                             'is_divergence_open_candidate',
                                                             'paired_divergence_opens_id',
                                                             'paired_divergence_opens_closing_price',
                                                             'paired_divergence_opens_rsi',
                                                             'is_divergence_high', 'rsi', 'is_entry_candidate',
                                                             'is_entry', 'symbol'])

            self.df_dict[symbol]['is_divergence_open_candidate'] = self.df_dict[symbol][
                'is_divergence_open_candidate'].astype(int)
            self.df_dict[symbol]['symbol'] = symbol

        # For each symbol, get Historical Data and listen for realtime data, by passing unique reqID
        for i, symbol in enumerate(self.symbols, start=1):
            self.subscribe_to_symbol(symbol, i)  # Pass a unique reqID for each symbol

        def get_mysql_engine():
            user = 'root'
            password = 'VZe1x2sF1HTyLp9r27Ka'
            host = 'localhost'
            port = 3306
            database = 'trading_bot_debug'
            engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")
            return engine

        try:
            self.mysql_engine = get_mysql_engine()
            print("Connected to MySQL database using SQLAlchemy")
        except Exception as ex:
            print("Error creating MySQL engine:", ex)

        # Uncomment the following line to drop tables if needed
        self.drop_tables_if_exist()

    def subscribe_to_symbol(self, symbol, reqID):
        # Define a contract for the given symbol
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "EUR"

        # Store the symbol in the sym_dict for later reference
        self.sym_dict[reqID] = symbol

        # Return the contract object
        return contract

    # Listen to socket in separate thread
    def run_loop(self):
        try:
            self.ib.run()
        except Exception as e:
            print(f"Error in run loop: {e}")
            traceback.print_exc()

    def place_order_if_entry_conditions_met(self, reqID, bar, symbol):
        if self.df_dict[symbol]['is_entry'].iloc[-2] == 1:
            # Bracket Order 2% Pro fit Target 1% Stop Loss
            profitTarget = bar.close * 1.005
            stopLoss = bar.close * 0.995
            quantity = 1
            bracket = self.bracket_order(orderId, "BUY", quantity, profitTarget, stopLoss, symbol)
            contract = Contract()
            contract.symbol = symbol.upper()
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "EUR"

            # Place the Bracket Order
            for o in bracket:
                o.ocaGroup = "OCA_" + str(orderId)
                o.ocaType = 2
                self.ib.placeOrder(o.orderId, contract, o)

            self.orderId += 3
            print("entered order confirmed")

    # Bracket Order Setup
    def bracket_order(self, parentOrderID, action, quantity, profitTarget, stopLoss, symbol):
        # Initial Entry
        # Create our IB Contract Object
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "EUR"
        # Create Parent Order / Initial Entry
        parent = Order()
        parent.orderId = parentOrderID
        parent.orderType = "MKT"
        parent.action = action
        parent.totalQuantity = quantity
        parent.transmit = False
        # Profit Target
        profitTargetOrder = Order()
        profitTargetOrder.orderId = parentOrderID + 1
        profitTargetOrder.orderType = "LMT"
        profitTargetOrder.action = "SELL"
        profitTargetOrder.totalQuantity = quantity
        profitTargetOrder.lmtPrice = round(profitTarget, 2)
        profitTargetOrder.transmit = False
        # Stop Loss
        stopLossOrder = Order()
        stopLossOrder.orderId = parentOrderID + 2
        stopLossOrder.orderType = "STOP"
        stopLossOrder.action = "SELL"
        stopLossOrder.totalQuantity = quantity
        stopLossOrder.auxPrice = round(stopLoss, 2)
        stopLossOrder.transmit = True

        bracketOrders = [parent, profitTargetOrder, stopLossOrder]
        return bracketOrders