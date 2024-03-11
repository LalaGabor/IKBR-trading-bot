import pandas
import traceback


class RealtimeDataManager:
    def __init__(self, bot):
        try:
            self.bot = bot
        except Exception as e:
            print(f"Error initializing RealtimeDataManager: {e}")
            traceback.print_exc()

    # start processing incoming realtime data
    def incoming_realtime_data(self, reqID, bar):
        try:
            symbol = self.bot.sym_dict[reqID]  # Fetch the symbol corresponding to the reqID
            self.handle_realtime_bars(bar, symbol)
        except Exception as e:
            print(f"Error with incoming_realtime_data: {e}")
            traceback.print_exc()

    # keep processing realtime data, in particular on bar close logic
    def handle_realtime_bars(self, bar, symbol):
        try:
            # Build realtime bars based on incoming data
            self.process_realtime_bars(bar, symbol)  # Either appends a new bar or updates an existing one
            # Store bar time of the incoming bar for logical handling of bar closes
            bar_time = bar.tick
            self.bar_logic_executed = False  # ensure the following conditional is only triggered once
            # On realtime Bar Close, perform the following...
            # TODO later, alter this logic for 30min bars. It will be minutes == 29/59 and seconds == 55
            if bar_time.second == 55:
                print("bar close logic triggered")
                print(bar_time)
                row_number = -1
                ##TODO this logic is potentially imprecise? Refactor to label incoming tick erroneous if seconds
                ## difference to now() > 60 seconds
                # Check if the thread started at a problematic start time, if yes, do not evaluate the first bar close
                if self.bot.threading_manager.start_time_causing_issues:
                    self.bot.mysql_connector.deduplication_of_partial_historical_data(symbol, row_number)
                    self.bot.threading_manager.start_time_causing_issues = False  # Once the erroneous first bar close
                    # has been handled, return to regular processing
                else:
                    self.bot.mysql_connector.deduplication_of_partial_historical_data(symbol, row_number)
                    self.bot.technical_analysis_manager.calculate_ta_indicators(symbol,
                                                                                row_number, bar, realtime=True)  #
                    # calculate the technical indicators
                    print(f"bar processed for {symbol}")
                    # Set the flag to True to ensure the logic is executed only once per bar
                    self.bar_logic_executed = True
        except Exception as e:
            print(f"Error with handle_realtime_bars: {e}")
            traceback.print_exc()
    # process realtime data for dataframe appending
    def process_realtime_bars(self, bar, symbol):
        try:
            # Check which rows in the Date column of the dataframe of the symbol are equal to incoming bar's date
            incoming_bars_date = self.bot.df_dict[symbol]['Date'] == bar.date
            # Append incoming data to dataframe, based on the bar's date
            if incoming_bars_date.any():  # if any rows in the Date column of the dataframe of the symbol
                # are equal to incoming bar's date, then:
                update_index = self.bot.df_dict[symbol].index[incoming_bars_date][-1]  # set update_index equal \
                # to the row of a matched date
                # Don't append 'Open'. Only use the first ticks' 'Open'
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
                # append the new_data Series
                self.bot.df_dict[symbol] = pandas.concat(
                    [self.bot.df_dict[symbol], pandas.DataFrame(new_data, index=[new_index])], ignore_index=True)
        except Exception as e:
            print(f"Error with process_realtime_bars: {e}")
            traceback.print_exc()
    # special handler for buffered realtime data, but seems superfluous now
    def handle_buffered_realtime_data(self, reqID, bar):
        try:
            symbol = self.bot.sym_dict[reqID]  # Fetch the symbol corresponding to the reqID
            self.bot.mysql_connector.deduplication_of_partial_historical_data(symbol)  # deletes the row in the DB of the
            # evaluated bar's date
            self.handle_realtime_bars(bar, symbol)
        except Exception as e:
            print(f"Error with process_realtime_bars: {e}")
            traceback.print_exc()
