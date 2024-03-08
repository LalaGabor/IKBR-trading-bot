import time
import traceback
import queue
import threading
import concurrent.futures
from datetime import datetime
import pytz


# Manages threads for incoming data
class ThreadingManager:
    def __init__(self, bot):
        try:
            self.bot = bot  # Communicate with bot instance

            self.thread_start_time = datetime.now()

            self.start_time_causing_issues = 0

        except Exception as e:
            print(f"Error with initializing ThreadingManager: {e}")
            traceback.print_exc()

    # Threading attributes are required to be defined before initializing threads
    def initialize_threading_attributes(self):
        try:
            for symbol in self.bot.symbols:  # for each symbol, reqID key/value pair in sym_dict....
                self.bot.threading_attributes_by_symbol[symbol] = {  # create a new dictionary of symbol specific
                    # dictionaries
                    'realtime_buffer': queue.Queue(),  # containing a queue
                    'buffer_lock': threading.Lock(),  # containing a lock
                    'historical_data_processed': False,  # containing a flag
                    'realtime_priority': False  # containing a flag
                }

        except Exception as e:
            print(f"Error with initializing ThreadingManager: {e}")
            traceback.print_exc()

    def start_threads(self):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2 * len(self.bot.symbols)) as executor:

                # Start historical and realtime threads using ThreadPoolExecutor
                all_threads = {executor.submit(self.historical_thread, symbol, i): symbol for i, symbol in
                               enumerate(self.bot.symbols, start=1)}
                print(f"started historical thread at {datetime.now()}")

                all_threads.update({executor.submit(self.realtime_thread, symbol, i): symbol for i, symbol in
                                    enumerate(self.bot.symbols, start=1)})
                print(f"started realtime thread at {datetime.now()}")

                self.thread_start_time = datetime.now(pytz.timezone("Europe/Berlin"))

                # Conditional checks if a tick arrived before start of thread time (which causes duplication issues)
                if self.thread_start_time.second in range (0,6):
                    self.start_time_causing_issues = 1
                    print(f" causing issues? {self.start_time_causing_issues}")

        except Exception as e:
            print(f"Error with start_threads: {e}")
            traceback.print_exc()

    def historical_thread(self, symbol, reqID):
        try:
            # listen for realtime data, this automatically triggers callback method historicalData
            contract = self.bot.subscribe_to_symbol(symbol, reqID)
            # listen for historical data
            self.bot.ib.reqHistoricalData(reqID, contract, "", "8000 S", "1 min", "TRADES", 1, 1, False, [])
            print(f"started historical thread for symbol {symbol}")

        except Exception as e:
            print(f"Exception in historical_thread for symbol {symbol}, reqID {reqID}: {e}")
        traceback.print_exc()

    def realtime_thread(self, symbol, reqID):
        try:
            # Get the contract object from subscribe to symbols
            contract = self.bot.subscribe_to_symbol(symbol, reqID)
            print(f"Realtime thread for symbol {symbol}, reqID: {reqID}: Contract: ({contract})")
            # listen for realtime data
            self.bot.ib.reqRealTimeBars(reqID, contract, 5, "TRADES", True, [])
            print(f"started realtime thread for symbol {symbol}")

        except Exception as e:
            print(f"Exception in realtime_thread for symbol {symbol}, reqID {reqID}: {e}")
            traceback.print_exc()