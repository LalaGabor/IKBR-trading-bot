import time
import traceback
import queue
import threading
import concurrent.futures


class ThreadingManager:
    def __init__(self, bot):
        self.bot = bot
    def initialize_threading_attributes(self):
        for symbol in self.bot.symbols:  # for each symbol, reqID key/value pair in sym_dict....
            self.bot.threading_attributes_by_symbol[symbol] = {  # create a new dictionary of symbol specific
                # dictionaries
                'realtime_buffer': queue.Queue(),  # containing a queue
                'buffer_lock': threading.Lock(),  # containing a lock
                'historical_data_processed': False,  # containing a flag
                'realtime_priority': False  # containing a flag
            }

    def start_threads(self):
        current_seconds = time.localtime().tm_sec

        # this conditional is a "lazy" workaround to the issue that starting the script in during the last tick
        # causes duplication issues
        if current_seconds in range(53, 60) or current_seconds in range(0, 3):
            # Calculate the remaining seconds until the next acceptable time (03 seconds)
            remaining_seconds = (3 - current_seconds) % 60

            # Wait for the remaining seconds
            time.sleep(remaining_seconds)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2 * len(self.bot.symbols)) as executor:
            # Start historical and realtime threads using ThreadPoolExecutor
            all_threads = {executor.submit(self.historical_thread, symbol, i): symbol for i, symbol in
                           enumerate(self.bot.symbols, start=1)}
            ##TODO is this comment out correct?
            all_threads.update({executor.submit(self.realtime_thread, symbol, i): symbol for i, symbol in
                                enumerate(self.bot.symbols, start=1)})

            # Wait for all threads to complete
            # concurrent.futures.wait(all_threads, timeout=None, return_when=concurrent.futures.ALL_COMPLETED)

    def historical_thread(self, symbol, reqID):
        try:
            # listen for realtime data, this automatically triggers callback method historicalData
            contract = self.bot.subscribe_to_symbol(symbol, reqID)
            # listen for historical data
            self.bot.ib.reqHistoricalData(reqID, contract, "", "8000 S", "1 min", "TRADES", 1, 1, False, [])
            print(f"started historical thread for symbol {symbol}")
        except Exception as e:
            print(f"Exception in historical_thread for symbol {symbol}, reqID {reqID}: {e}")

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