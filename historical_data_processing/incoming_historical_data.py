import pandas
import traceback


class HistoricalDataManager:
    def __init__(self, bot):
       self.bot = bot
    def incoming_historical_data(self, reqID, bar):
        symbol = self.bot.sym_dict[reqID]  # Fetch the symbol corresponding to the reqID
        self.process_historical_bars(bar, symbol)
        row_number = -1
        self.bot.technical_analysis_manager.calculate_ta_indicators(symbol, row_number)

    def process_historical_bars(self, bar, symbol):
        try:
            if self.bot.df_dict[symbol].empty:
                new_index = 0  # You can use 0 or any default value if the DataFrame is empty
            else:
                new_index = self.bot.df_dict[symbol].index[-1] + 1
            # assign the bar data
            self.bot.currentBar.open = bar.open
            self.bot.currentBar.high = bar.high
            self.bot.currentBar.low = bar.low
            self.bot.currentBar.close = bar.close
            self.bot.currentBar.volume = bar.volume
            self.bot.currentBar.date = bar.date
            self.bot.currentBar.tick = bar.date
            # append the bar data
            new_data = {'Open': self.bot.currentBar.open,
                        'High': self.bot.currentBar.high,
                        'Low': self.bot.currentBar.low,
                        'Close': self.bot.currentBar.close,
                        'Volume': self.bot.currentBar.volume,
                        'Date': self.bot.currentBar.date,
                        'Tick': self.bot.currentBar.tick,
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