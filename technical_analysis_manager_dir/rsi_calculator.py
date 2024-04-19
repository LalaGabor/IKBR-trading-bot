import ta
from ta.momentum import rsi
import traceback


class RSICalculator:

    @staticmethod
    def calculate_rsi(closes, window=14):
        try:
            # Use the ta.momentum method to ingest a dataframe column (pandas Series) of closes and output a dataframe
            # column (pandas Series) of rsi values. It accepts closing prices with the datatype float and outputs
            # with the same datatype (float)
            return ta.momentum.rsi(closes, window=window)

        except Exception as e:
            print(f"Error with calculate_rsi: {e}")
            traceback.print_exc()

    @staticmethod
    def append_rsi_to_dataframe(dataframe, closes_column_name='Close', rsi_column_name='rsi', window=14):
        try:
            # Define the pandas Series (dataframe Column) containing the closing prices to be evaluated for rsi
            closes = dataframe[closes_column_name].astype(float)
            # Store the rsi values calculated by the calculate_rsi method in rsi_values
            rsi_values = RSICalculator.calculate_rsi(closes, window=window)

            # Check if there is at least one row in the DataFrame
            if not dataframe.empty:
                # Assign the index value of the most recent row to last_row_index
                last_row_index = dataframe.index[-1]
                # At the last row of the target data frame, find the column for rsi and set it equal to the values
                # stored in rsi_values
                dataframe.at[last_row_index, rsi_column_name] = rsi_values.iloc[-1]

        except Exception as e:
            print(f"Error with append_rsi_to_dataframe: {e}")
            traceback.print_exc()