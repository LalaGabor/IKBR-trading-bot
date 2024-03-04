import traceback
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from datetime import datetime
import threading_manager
import queue
import pytz
from bot import Bar

"""""""""""""""
This file manages the creation and connection to an ibapi TWS client and the adaptation of relevant callback methods
"""""""""""""""

class IBApi(EWrapper, EClient):
    def __init__(self, bot):
        # Build IBApi instance using the parent class EClient (provided in ibapi package)
        # The 'self' parameter represents the instance being created
        EClient.__init__(self, self)

        # Store a reference to the Bot instance
        # This allows IBApi to communicate with the Bot, especially for passing req_IDs
        self.bot = bot

    # Gets historical data, when it is made available
    # It is made available by ib.reqHistoricalData
    def historicalData(self, reqId, bar):
        try:
            # Convert date and pass data to the Bot
            bar.date = datetime.strptime(bar.date, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))
            # get the symbol key from the reqId value in the sym_dict dictionary
            symbol = self.bot.sym_dict[reqId]
            # for debugging print(self.bot.threading_attributes_by_symbol)
            # Check if threading_manager attributes for the symbol exist, if not, create them
            ##TODO update to reference threading_manager class object
            if symbol not in self.bot.threading_attributes_by_symbol:
                self.bot.threading_attributes_by_symbol[symbol] = {
                    'realtime_buffer': queue.Queue(),  # Buffers incoming realtime data
                    'buffer_lock': threading_manager.Lock(),  # Lock to alternate between realtime & historical threads
                    'historical_data_processed': False,  # Flag to indicate data processing step
                    'realtime_priority': False  # Initialize a flag to indicate the priority
                }
                # print(f"added threading_manager attributes for {symbol}")
            # Pass the reqID, bar, and False boolean (to indicate that data is historical)
            ##TODO update to reference historical data class object
            self.bot.incoming_historical_data(reqId, bar)
        except Exception as e:
            print(e)

    # On Historical Data End
    def historicalDataEnd(self, reqId, start, end):
        symbol = self.bot.sym_dict[reqId]
        print(f"Historical Data Request {reqId} completed from {start} to {end}")
        try:
            ##TODO update to reference threading_manager class object
            with self.bot.threading_attributes_by_symbol[symbol]['buffer_lock']:  # set context manager using buffer lock
                # print(self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].queue)  # Print the
                # contents of the queue
                ##TODO update to reference threading_manager class object
                if not self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].empty():
                    while not self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].empty():
                        ## TODO where is bar coming from?
                        reqID, bar = self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].get()

                        self.bot.handle_buffered_realtime_data(reqID, bar)
                        row_number = -2
                        self.bot.calculate_ta_indicators(symbol, row_number)
                        print(f"processed buffered data for {symbol}")

            self.bot.mysql_connector.deduplication_of_partial_historical_data(symbol)

            ##TODO update to reference threading_manager class object
            # Set the flag to indicate that historical data processing is completed
            if not self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed']:
                self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed'] = True

        except Exception as e:
            print(f"Error in historicalDataEnd: {e}")
            traceback.print_exc()

    # Get the next order id that can be used
    def nextValidId(self, nextorderID):
        global orderId
        orderId = nextorderID
        print(f"Next valid order ID received: {nextorderID}")

    # Gets realtime data, when it is made available
    # It is made available by ib.reqRealTimeBars
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        try:
            symbol = self.bot.sym_dict[reqId]  # get the symbol related to incoming data
            # While historical data is processing, buffer any incoming real-time data
            ##TODO update to reference threading_manager class object
            if not self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed']:
                #print("historical data not finished yet")
                #print(self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed'])

                # TODO ensure that realtime data has priority on the buffer

                # Lock to ensure thread safety when accessing the buffer
                ##TODO update to reference threading_manager class object
                with self.bot.threading_attributes_by_symbol[symbol]['buffer_lock']:
                    try:
                        time1 = datetime.fromtimestamp(time).strftime(
                            "%Y%m%d %H:%M:00")  # Convert to string with seconds set to 0 for grouping realtime on bar data
                        # print(f"Type of 'time': {type(time)}, Value of 'time': {time}")
                        time1 = datetime.strptime(time1, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))
                        tick = datetime.fromtimestamp(time).strftime(
                            "%Y%m%d %H:%M:%S")  # Convert to string with seconds set to 0 for grouping realtime on bar data
                        # print(f"Type of 'time': {type(time)}, Value of 'time': {time}")
                        tick = datetime.strptime(tick, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))
                        # self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].put((reqId, Bar(open_,
                        # high, low, close, volume, time1, tick)))
                        #print(f"Buffered realtime data for reqId {reqId}")
                    except Exception as e:
                        print(f"Error buffering realtime data: {e}")

        # When  historical data is finished processing, process incoming real-time bars immediately
            ##TODO update to reference threading_manager class object
            if self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed']:
                #print("historical data is finished")
                try:
                    # Pass realtime bar data back to the Bot object
                    #print(f"Type of 'time': {type(time)}, Value of 'time': {time}")
                    # TODO You will need to adapt the code for different minute intervals here
                    time1 = datetime.fromtimestamp(time).strftime(
                        "%Y%m%d %H:%M:00")  # Convert to string with seconds set to 0 for grouping realtime on bar data
                    #print(f"Type of 'time': {type(time)}, Value of 'time': {time}")
                    time1 = datetime.strptime(time1, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))
                    tick = datetime.fromtimestamp(time).strftime(
                        "%Y%m%d %H:%M:%S")  # Convert to string with seconds set to 0 for grouping realtime on bar data
                    # print(f"Type of 'time': {type(time)}, Value of 'time': {time}")
                    tick = datetime.strptime(tick, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))
                   # print(f"Type of 'time': {type(time)}, Value of 'time': {time}")
                    ##TODO update to reference realtime data class object
                    ##TODO solve reference to bar
                    self.bot.incoming_realtime_data(reqId,
                                                    Bar(open_, high, low, close, volume, time1, tick))
                    #print(f"Processed realtime data for reqId {reqId}")
                except Exception as e:
                    print(f"Error processing realtime data: {e}")

        except Exception as e:
            print(f"Error buffering realtime data: {e}")
        # print("Released buffer_lock")

    # Handle errors
    def error(self, id, errorCode, errorMsg):
        print(f"Error {errorCode} for ID {id}: {errorMsg}")