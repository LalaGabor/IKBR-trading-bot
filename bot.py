from datetime import datetime
import traceback
import pytz
import threading
import time
import pandas
from ibapi.contract import Contract
import database_manager_dir
import historical_data_manager_dir
import realtime_data_manager_dir
import technical_analysis_manager_dir
import threading_manager
import order_manager_dir
from ikbr_client_dir.ikbr_client import IBApi


##TODO Fix Divergence bug in source script
##TODO Divergence Opens do not deactivate old opens fast enough? Check with backtest scripts for required logic
##todo clean up comments

# Suppress the SettingWithCopy warning
pandas.options.mode.chained_assignment = None

#Set script level parameters
symbol_list = ["ENEL"] #, "ENI"]#, "ISP", "UCG", "G", "PIRC", "SPM", "UNI", "BAMI", "LDO"]


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
    sym_dict = {}  # stores a symbol, reqID pair

    # The init is automatically run when an instance of the class is created
    def __init__(self, symbol_list, create_clients=True):
        try:
            # Ingest the symbol_list
            self.symbols = symbol_list

            # Set the create_clients Flag (to allow for tests without the client running)
            self.create_clients = create_clients
            if self.create_clients:
                try:
                    # Connect to TWS API on init
                    self.ib = IBApi(self, "Communicator Client")  # Note: you can not create multiple bot objects, as TWS API
                    # Note: IBApi won't accept multiple clients on same port
                    self.ib.connect("127.0.0.1", 7497, 1)  # Pass connection details to TWS API
                    print("Connected to Interactive Brokers")
                    time.sleep(1)
                except Exception as e:
                    print(f"Error in initializing IB client: {e}")
                    traceback.print_exc()

            # initialize a DatabaseManager object, pass bot instance to object on init
            # this object creates an engine that connects to local DB on init
            self.mysql_connector = database_manager_dir.DatabaseManager(self)

            if self.create_clients:
                try:
                    # initialize an IBAPI object, pass bot instance to object on init
                    self.ibapi_client = IBApi(self, "Order Execution Client")
                except Exception as e:
                    print(f"Error in initializing IB client: {e}")
                    traceback.print_exc()

            # initialize a ThreadingManager object, pass bot instance to object on init
            self.threading_manager = threading_manager.ThreadingManager(self)

            # initialize a HistoricalDataManager object, pass bot instance to object on init
            self.historical_data_manager = historical_data_manager_dir.HistoricalDataManager(self)

            # initialize a RealtimeDataManager object, pass bot instance to object on init
            self.realtime_data_manager = realtime_data_manager_dir.RealtimeDataManager(self)

            # initialize a TechnicalAnalysisProcessor object, pass bot instance to object on init
            self.technical_analysis_manager = technical_analysis_manager_dir.TechnicalAnalysisProcessor(self)

            # initialize an OrderManager object, pass bot instance to object on init
            self.order_manager = order_manager_dir.OrderManager(self)


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
    def get_symbols_contract_object(self, symbol):
        try:
            contract = Contract()  # using ibapi.contract constructor
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "EUR"

            # Return the contract object, which is required to call reqHistoricalData & reqRealTimeBars
            return contract

        except Exception as e:
            print(f"Error getting contract for {symbol}: {e}")
            traceback.print_exc()

    def subscribe_to_symbol(self, symbol, reqID):
        try:# Define a contract for the given symbol

            # Store the symbol in the sym_dict for later reference
            self.sym_dict[reqID] = symbol

        except Exception as e:
            print(f"Error subscribing to symbol: {e}")
            traceback.print_exc()

    # Open a communication thread with TWS API for handling connection & order placement
    # created on init of bot class instance
    def run_loop(self):
        if self.create_clients == True:
            try:
                self.ib.run()
            except Exception as e:
                print(f"Error in starting listener run_loop: {e}")
                traceback.print_exc()


# Learning about if __name__ == "__main"
"""
## Learning for Sebo
## 'if __name__ == "__main__" is to prevent global code execution
## Typcially, when code is imported, it actually runs all the code in the imported file function/class definitions of
# course do not trigger any executions but any code outside these constructs, e.g. calling a function, 
# will be triggered, if not wrapped inside the conditional.
## Note: when python imports a module, it sets __name__ to the name of the module being imported. But when python 
# executes a module, it sets __name__ equal to __main__, thus the logic of the conditional
"""
# Script execution
if __name__ == "__main__":
    #TODO add if name == main conditional
    # Start bot, this opens connection to TWS API
    bot = Bot(symbol_list)
    print("start bot")
    # Get required attributes to start incoming data threads
    bot.threading_manager.initialise_threading_attributes()
    print("initialising threads")
    # Start ingesting data from API, which subsequently triggers order placement
    bot.threading_manager.start_threads()
    print("started threads")
