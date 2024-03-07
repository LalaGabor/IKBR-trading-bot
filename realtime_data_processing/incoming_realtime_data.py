import pandas
from datetime import datetime

class RealtimeDataManager:
    def __init__(self, bot):
        self.bot = bot
    def incoming_realtime_data(self, reqID, bar):

        symbol = self.bot.sym_dict[reqID]  # Fetch the symbol corresponding to the reqID
        # self.deduplication_of_partial_historical_data(symbol)  # deletes the row in the DB of the evaluated bar's date
        self.handle_realtime_bars(bar, symbol)
        ##TODO update reference to bot object??
        self.bot.order_manager.place_order_if_entry_conditions_met(reqID, bar, symbol)
    def handle_realtime_bars(self, bar, symbol):
        # Build realtime bars based on incoming data
        self.process_realtime_bars(bar, symbol)  # Either appends a new bar or updates an existing one
        # Store bar time of the incoming bar for logical handling of bar closes
        bar_time = bar.tick
        self.bar_logic_executed = False  # ensure the following conditional is only triggered once
        print(f"bar tick is {bar_time}")
        print(f"now is {datetime.now()}")
        # On realtime Bar Close, perform the following...
        # TODO later, alter this logic for 30min bars. It will be minutes == 29/59 and seconds == 55
        if bar_time.second == 55:
            print("bar close logic triggered")
            #TODO check if dataframe stores duplicates
            print(f" print all rows in dataframe where 'Tick' column equals the closing tick: "
                  f"{self.bot.df_dict[symbol][self.bot.df_dict[symbol]['Tick'] == bar_time]}") # checks if there are
            # any  duplicates in dataframe
            row_number = -1
            self.bot.mysql_connector.deduplication_of_partial_historical_data(symbol)
            self.bot.technical_analysis_manager.calculate_ta_indicators(symbol, row_number)  # calculate the technical indicators
            print(f"bar processed for {symbol}")
            # Set the flag to True to ensure the logic is executed only once per bar
            self.bar_logic_executed = True

    def process_realtime_bars(self, bar, symbol):
        # Check which rows in the Date column of the dataframe of the symbol are equal to incoming bar's date
        incoming_bars_date = self.bot.df_dict[symbol]['Date'] == bar.date

        # IB API team confirmed that TWS and real time bars have slight differences due to exclusion of some NBBO orders
        # Append incoming data to dataframe, based on the bar's date
        if incoming_bars_date.any():  # if any rows in the Date column of the dataframe of the symbol
            # are equal to incoming bar's date, then:
            update_index = self.bot.df_dict[symbol].index[incoming_bars_date][-1]  # set update_index equal \
            # to the row of a matched date
            # Don't append open, only use the first ticks open
            self.bot.df_dict[symbol].loc[update_index, 'High'] = max(bar.high,
                                                                 self.bot.df_dict[symbol].loc[update_index, 'High'])
            self.bot.df_dict[symbol].loc[update_index, 'Low'] = min(bar.low,
                                                                self.bot.df_dict[symbol].loc[update_index, 'Low'])
            self.bot.df_dict[symbol].loc[update_index, 'Close'] = bar.close
            self.bot.df_dict[symbol].loc[update_index, 'Volume'] += bar.volume  # Add the volume
            self.bot.df_dict[symbol].loc[update_index, 'Date'] = bar.date
            self.bot.df_dict[symbol].loc[update_index, 'Tick'] = bar.tick
        # Else append a new row for the current date
        else:
            new_index = len(self.bot.df_dict[symbol])
            new_data = {'Open': bar.open,
                        'High': bar.high,
                        'Low': bar.low,
                        'Close': bar.close,
                        'Volume': bar.volume,
                        'Date': bar.date,
                        'Tick': bar.tick,
                        'is_divergence_open_candidate': 0,
                        'paired_divergence_opens_id': 0,
                        'paired_divergence_opens_closing_price': 0,
                        'paired_divergence_opens_rsi': 0,
                        'is_divergence_high': 0,
                        'rsi': 0,
                        'symbol': symbol}

            self.bot.df_dict[symbol] = pandas.concat([self.bot.df_dict[symbol], pandas.DataFrame(new_data, index=[new_index])], ignore_index=True)
    def handle_buffered_realtime_data(self, reqID, bar):

        symbol = self.bot.sym_dict[reqID]  # Fetch the symbol corresponding to the reqID
        self.bot.mysql_connector.deduplication_of_partial_historical_data(symbol)  # deletes the row in the DB of the
        # evaluated bar's date
        self.handle_realtime_bars(bar, symbol)
