import datetime
import traceback
import pytz
from ikbr_client import IBApi
import threading
import time
import pandas
from ibapi.contract import Contract
from database import DatabaseManager
from historical_data_processing import HistoricalDataManager
from realtime_data_processing import RealtimeDataManager
from technical_analysis import TechnicalAnalysisProcessor
from threading_manager import ThreadingManager
from order_manager_dir import OrderManager


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
        # initialize a DatabaseManager object, pass bot instance to object on init
        # this object creates an engine that connects to local DB on init
        self.mysql_connector = DatabaseManager(self)
        # initialize an IBAPI object, pass bot instance to object on init
        self.ibapi_client = IBApi(self)
        # initialize a ThreadingManager object, pass bot instance to object on init
        self.threading_manager = ThreadingManager(self)
        # initialize a HistoricalDataManager object, pass bot instance to object on init
        self.historical_data_manager = HistoricalDataManager(self)
        # initialize a RealtimeDataManager object, pass bot instance to object on init
        self.realtime_data_manager = RealtimeDataManager(self)
        # initialize a TechnicalAnalysisProcessor object, pass bot instance to object on init
        self.technical_analysis_manager = TechnicalAnalysisProcessor(self)
        # initialize an OrderManager object, pass bot instance to object on init
        self.order_manager = OrderManager(self)

        # Connect to TWS API on init
        self.ibapi_client.connect("127.0.0.1", 7497, 1)
        print("Connected to Interactive Brokers")

        ## TODO move this to threading manager
        # Start a separate thread for IB communication
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)

        # Create a bot specific dictionary to store threading attributes
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

        # Get a unique reqID for each symbol
        for i, symbol in enumerate(self.symbols, start=1):
            self.subscribe_to_symbol(symbol, i)

    def subscribe_to_symbol(self, symbol, reqID):
        # Define a contract for the given symbol
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "EUR"

        # Store the symbol in the sym_dict for later reference
        self.sym_dict[reqID] = symbol

        ## TODO, do I need this??
        # Return the contract object
        return contract

    # Listen to socket in separate thread, called on init of bot class instance
    def run_loop(self):
        try:
            self.ib.run()
        except Exception as e:
            print(f"Error in run loop: {e}")
            traceback.print_exc()


# Start bot
bot = Bot()
bot.threading_manager.initialize_threading_attributes()
bot.threading_manager.start_threads()