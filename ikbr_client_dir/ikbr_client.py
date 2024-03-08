import traceback
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from datetime import datetime
import pytz
#from bot import Bar

"""""""""""""""
This file manages the creation and connection to an ibapi TWS client and the adaptation of relevant callback methods
"""""""""""""""
class Bar:
    def __init__(self, open_, high, low, close, volume, date, tick):
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.date = date
        self.tick = tick


class IBApi(EWrapper, EClient):
    def __init__(self, bot):
        try:
            # Build IBApi instance using the parent class EClient (provided in ibapi package)
            # The 'self' parameter represents the instance being created
            EClient.__init__(self, self)

            # Store a reference to the Bot instance
            # This allows IBApi to communicate with the Bot, especially for passing req_IDs
            self.bot = bot
        except Exception as e:
            print(f"Error initializing IBApi object: {e}")
            traceback.print_exc()
    # Gets historical data, when it is made available
    # It is made available by ib.reqHistoricalData
    def historicalData(self, reqId, bar):
        try:
            # Convert date and pass data to the Bot
            bar.date = datetime.strptime(bar.date, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))
            self.bot.historical_data_manager.incoming_historical_data(reqId, bar)
        except Exception as e:
            print(f"Error with historicalData callback method: {e}")
            traceback.print_exc()

    # On Historical Data End
    def historicalDataEnd(self, reqId, start, end):
        symbol = self.bot.sym_dict[reqId]  # get the relevant symbol
        print(f"Historical Data Request {reqId} completed from {start} to {end}")
        """Note the buffer appears superfluous, but is kept in code for now, as might be added back later"""
        try:
            with self.bot.threading_attributes_by_symbol[symbol]['buffer_lock']:  # set context manager using buffer lock
                if not self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].empty():
                    while not self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].empty():
                        reqID, bar = self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].get()
                        self.bot.realtime_data_manager.handle_buffered_realtime_data(reqID, bar)
                        row_number = -2
                        self.bot.calculate_ta_indicators(symbol, row_number)
                        print(f"processed buffered data for {symbol}")

            # Set the flag to indicate that historical data processing is completed
            if not self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed']:
                self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed'] = True

        except Exception as e:
            print(f"Error in historicalDataEnd callback method: {e}")
            traceback.print_exc()

    #TODO is this needed?
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
            if not self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed']:

                # TODO ensure that realtime data has priority on the buffer
                # TODO why isn't buffer required?

                # Lock to ensure thread safety when accessing the buffer
                with self.bot.threading_attributes_by_symbol[symbol]['buffer_lock']:
                    try:
                        time1 = datetime.fromtimestamp(time).strftime(
                            "%Y%m%d %H:%M:00")  # Convert to string with seconds set to 0 for grouping realtime on bar data
                        time1 = datetime.strptime(time1, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))
                        tick = datetime.fromtimestamp(time).strftime(
                            "%Y%m%d %H:%M:%S")
                        tick = datetime.strptime(tick, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))
                        #self.bot.threading_attributes_by_symbol[symbol]['realtime_buffer'].put((reqId, Bar(open_,
                        # high, low, close, volume, time1, tick)))

                    except Exception as e:
                        print(f"Error buffering realtime data: {e}")
                        traceback.print_exc()

        # When  historical data is finished processing, process incoming real-time bars immediately
            if self.bot.threading_attributes_by_symbol[symbol]['historical_data_processed']:
                try:
                    # TODO You will need to adapt the code for different minute intervals here
                    time1 = datetime.fromtimestamp(time).strftime(
                        "%Y%m%d %H:%M:00")  # Convert to string with seconds set to 0 for grouping realtime on bar data

                    time1 = datetime.strptime(time1, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))

                    tick = datetime.fromtimestamp(time).strftime(
                        "%Y%m%d %H:%M:%S")
                    tick = datetime.strptime(tick, "%Y%m%d %H:%M:%S").astimezone(pytz.timezone("Europe/Berlin"))

                    # begin processing the incoming real time data
                    self.bot.realtime_data_manager.incoming_realtime_data(reqId,
                                                    Bar(open_, high, low, close, volume, time1, tick))

                except Exception as e:
                    print(f"Error processing realtime data: {e}")
                    traceback.print_exc()

        except Exception as e:
            print(f"Error processing realtime data: {e}")
            traceback.print_exc()

    # Handle errors
    def error(self, id, errorCode, errorMsg):
        print(f"Error {errorCode} for ID {id}: {errorMsg}")