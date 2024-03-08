from datetime import datetime
import traceback
import pytz
import threading
import time
import pandas
from ibapi.contract import Contract
import database
import historical_data_processing
import realtime_data_processing
import technical_analysis
import threading_manager
import order_manager_dir
from ikbr_client_dir.ikbr_client import IBApi


##TODO Fix Divergence bug in source script
##TODO Divergence Opens do not deactivate old opens fast enough? Check with backtest scripts for required logic


## todo merge branch with main
##todo clean up comments
##todo make some magic numbers global/class variables
##todo refactor reference to parent variables, if possible
##todo fix Error processing realtime data: place_order_if_entry_conditions_met() takes 3 positional arguments but 4 were given
##todo add try except everywhere


# Suppress the SettingWithCopy warning
pandas.options.mode.chained_assignment = None


# The Bar constructor is used to format incoming data from the TWS API
class Bar:
    def __init__(self, open_, high, low, close, volume, date, tick):
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.date = date
        self.tick = tick


# Bot ingests incoming data and places orders on TWS API if technical analysis conditions are met
class Bot:
    bar_size = 1  # bar_size defines the minute length of the incoming bars
    historical_look_back_period = '8000 S'  # defines how many historical bars to ask for (must be minimum 60 bars, ...
    # ... so the value must be adapted to bar_size)
    df_dict = {}  # Dictionary to store DataFrames for each symbol
    reqID = 1
    symbols = ["ENEL"]  # , "ENI", "ISP", "UCG", "G", "PIRC", "SPM", "UNI", "BAMI", "LDO"]
    sym_dict = {}  # stores a symbol, reqID pair

    # what is automatically run when an instance of the class is created
    def __init__(self):
        try:
            # initialize a DatabaseManager object, pass bot instance to object on init
            # this object creates an engine that connects to local DB on init
            self.mysql_connector = database.DatabaseManager(self)
            # initialize an IBAPI object, pass bot instance to object on init
            self.ibapi_client = IBApi(self)
            # initialize a ThreadingManager object, pass bot instance to object on init
            self.threading_manager = threading_manager.ThreadingManager(self)
            # initialize a HistoricalDataManager object, pass bot instance to object on init
            self.historical_data_manager = historical_data_processing.HistoricalDataManager(self)
            # initialize a RealtimeDataManager object, pass bot instance to object on init
            self.realtime_data_manager = realtime_data_processing.RealtimeDataManager(self)
            # initialize a TechnicalAnalysisProcessor object, pass bot instance to object on init
            self.technical_analysis_manager = technical_analysis.TechnicalAnalysisProcessor(self)
            # initialize an OrderManager object, pass bot instance to object on init
            self.order_manager = order_manager_dir.OrderManager(self)

            # Connect to TWS API on init
            self.ib = IBApi(self)  # Note: you can not create multiple bot objects, as TWS API won't accept multiple
            # clients on same port
            self.ib.connect("127.0.0.1", 7497, 1)  # pass connection details to TWS API
            print("Connected to Interactive Brokers")

            # TODO move this to threading manager
            # Start a separate thread for IB communication
            ib_thread = threading.Thread(target=self.run_loop, daemon=True)
            ib_thread.start()
            time.sleep(1)

            # Create a bot specific dictionary to store threading attributes
            self.threading_attributes_by_symbol = {}  # stores buffer, lock, flags for symbol specific threads

        except Exception as e:
            print(f"Error processing initializing bot object: {e}")
            traceback.print_exc()

        try:
        # For each symbol, initialize a DataFrame with necessary columns
            for symbol in self.symbols:  # iterate over class variable 'symbols'
                self.df_dict[symbol] = pandas.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Date', 'Tick',
                                                                 'is_divergence_open_candidate',
                                                                 'paired_divergence_opens_id',
                                                                 'paired_divergence_opens_closing_price',
                                                                 'paired_divergence_opens_rsi',
                                                                 'is_divergence_high', 'rsi', 'is_entry_candidate',
                                                                 'is_entry', 'symbol'])
        except Exception as e:
            print(f"Error creating dataframe: {e}")
            traceback.print_exc()

        # Store a unique reqID for each symbol in sym_dict
        for i, symbol in enumerate(self.symbols, start=1):
            self.subscribe_to_symbol(symbol, i)

    # Dual-purpose method, link symbol & reqID as well as return the contract object
    def subscribe_to_symbol(self, symbol, reqID):
        try:# Define a contract for the given symbol
            contract = Contract()  # using ibapi.contract constructor
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "EUR"

            # Store the symbol in the sym_dict for later reference
            self.sym_dict[reqID] = symbol

            # Return the contract object, which is required to call reqHistoricalData & reqRealTimeBars
            return contract

        except Exception as e:
            print(f"Error subscribing to symbol: {e}")
            traceback.print_exc()
    # Open a communication thread with TWS API for handling connection & order placement
    # created on init of bot class instance
    def run_loop(self):
        try:
            self.ib.run()
        except Exception as e:
            print(f"Error in starting listener run_loop: {e}")
            traceback.print_exc()

#TODO add if name == main conditional
# Start bot, this opens connection to TWS API
bot = Bot()
# Get required attributes to start incoming data threads
bot.threading_manager.initialize_threading_attributes()
# Start ingesting data from API, which subsequently triggers order placement
bot.threading_manager.start_threads()
