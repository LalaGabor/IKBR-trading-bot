from technical_analysis import EntryCalculator, DivergenceCalculator, RSICalculator
from database import DatabaseManager
import traceback


class TechnicalAnalysisProcessor:
    def __init__(self, bot):
        # Store a reference to the Bot instance
        # This allows DatabaseInteraction to communicate with the Bot, especially for passing df_dict
        self.bot = bot
        self.divergence_calc = DivergenceCalculator()
        self.rsi_calc = RSICalculator()
        self.entry_calc = EntryCalculator()

    def calculate_ta_indicators(self, symbol, row_number):

        # Calculate the bots dataframe's 'rsi' column using the RSICalculator class, by passing the 'Close' column
        self.bot.df_dict[symbol]['rsi'] = self.rsi_calc.calculate_rsi(self.bot.df_dict[symbol]['Close'])

        # calculate divergence, first get the open candidates (local peaks)
        try:
            self.divergence_calc.get_open_candidate(self.bot.df_dict[symbol], row_number)
        except Exception as e:
            print(f"Error in get_open_candidates_nearest_open: {e}")
            traceback.print_exc()

        # Next, identify close candidates, for given open candidates
        try:
            self.divergence_calc.get_close_candidates_nearest_open(self.bot.df_dict[symbol], row_number)
        except Exception as e:
            print(f"Error in get_close_candidates_nearest_open: {e}")
            traceback.print_exc()

        # Next, ensure the close is not also an open
        try:
            self.divergence_calc.limit_divergence_to_accepted_row(self.bot.df_dict[symbol], row_number)
        except Exception as e:
            print(f"Error in limit_divergence_to_accepted_row: ")
            traceback.print_exc()

        # Next confirm that open + close candidate fulfill divergence criteria
        try:
            self.divergence_calc.calculate_divergence(self.bot.df_dict[symbol], row_number)
        except Exception as e:
            print(f"Error in calculate_divergence: {e}")
            traceback.print_exc()

        # Find the entry candidates, rows that meet strategy criteria
        try:
            self.entry_calc.get_entry_candidates(self.bot.df_dict[symbol], row_number)
        except Exception as e:
            print(f"Error in calculate_divergence: {e}")
            traceback.print_exc()

        # Limit entry rows to first in local tick range
        try:
            self.entry_calc.get_entry_row(self.bot.df_dict[symbol], row_number)
        except Exception as e:
            print(f"Error in calculate_divergence: {e}")
            traceback.print_exc()

        # Append the incoming row
        incoming_row = self.bot.df_dict[symbol].iloc[row_number]  # Define the incoming row
        # Use the bots inited connector object to append to the database
        self.bot.mysql_connector.append_data_to_mysql(incoming_row, symbol)
