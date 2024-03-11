import pandas
import traceback

pandas.options.mode.chained_assignment = None  # Suppress the SettingWithCopy warning


class HistoricalDataManager:
    def __init__(self, bot):
        try:
            self.bot = bot
        except Exception as e:
            print(f"Error initializing HistoricalDataManager: {e}")
            traceback.print_exc()
    def incoming_historical_data(self, reqID, bar):
        try:
            symbol = self.bot.sym_dict[reqID]  # Fetch the symbol corresponding to the reqID
            self.process_historical_bars(bar, symbol)
            row_number = -1
            self.bot.technical_analysis_manager.calculate_ta_indicators(symbol, row_number)
        except Exception as e:
            print(f"Error with incoming_historical_data: {e}")
            traceback.print_exc()
    def process_historical_bars(self, bar, symbol):
        try:
            if self.bot.df_dict[symbol].empty:
                new_index = 0  # You can use 0 or any default value if the DataFrame is empty
            else:
                new_index = self.bot.df_dict[symbol].index[-1] + 1
            # append the bar data using the above index for label based append
            new_data = {'Open': bar.open,
                        'High': bar.high,
                        'Low': bar.low,
                        'Close': bar.close,
                        'Volume': bar.volume,
                        'Date': bar.date,
                        'Tick': bar.date,
                        'is_divergence_open_candidate': 0,
                        'paired_divergence_opens_id': 0,
                        'paired_divergence_opens_closing_price': 0,
                        'paired_divergence_opens_rsi': 0,
                        'is_divergence_high': 0,
                        'rsi': 0,
                        'symbol': symbol}
            self.bot.df_dict[symbol].loc[new_index] = new_data

        except Exception as e:
            print(f"Error in handle_historical_bar: {e}")
            traceback.print_exc()
