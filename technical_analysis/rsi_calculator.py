import ta
from ta.momentum import rsi
import traceback


class RSICalculator:

    @staticmethod
    def calculate_rsi(closes, window=14):
        try:
            return ta.momentum.rsi(closes, window=window)

        except Exception as e:
            print(f"Error with calculate_rsi: {e}")
            traceback.print_exc()
    @staticmethod
    def append_rsi_to_dataframe(dataframe, closes_column_name='Close', rsi_column_name='rsi', window=14):
        try:
            closes = dataframe[closes_column_name].astype(float)
            rsi_values = RSICalculator.calculate_rsi(closes, window=window)

            # Check if there is at least one row in the DataFrame
            if not dataframe.empty:
                # Assuming 'Date' column is present in the DataFrame
                last_row_index = dataframe.index[-1]
                dataframe.at[last_row_index, rsi_column_name] = rsi_values.iloc[-1]

        except Exception as e:
            print(f"Error with append_rsi_to_dataframe: {e}")
            traceback.print_exc()