import pandas
import traceback
pandas.options.mode.chained_assignment = None  # Suppress the SettingWithCopy warning

class EntryCalculator:

    # Find rows which meet the entry conditions
    def get_entry_candidates(self, pandas_dataframe, row_number):
        try:
            # Assuming 'Date' column is in datetime format
            if not pandas_dataframe.empty:
                last_row = pandas_dataframe.iloc[row_number]

                if last_row['rsi'] >= 65 and last_row['is_divergence_high'] == 1:
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry_candidate'] = 1

                else:
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry_candidate'] = 0

        except Exception as e:
            print(f"Error with get_entry_candidates realtime data: {e}")
            traceback.print_exc()


    # Find rows which are accepted entries
    def get_entry_row(self, pandas_dataframe, row_number):
        try:
            if not pandas_dataframe.empty:
                # Assuming 'Date' column is in datetime format
                last_row = pandas_dataframe.iloc[row_number]

                if 'is_entry_candidate' in pandas_dataframe.columns:

                    if pandas_dataframe.loc[pandas_dataframe.index[row_number - 5:row_number], 'is_entry_candidate'].eq(1).any():
                        pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry'] = 0

                    elif pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry_candidate'] == 1:
                        pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry'] = 1

                    else:
                        pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry'] = 0

        except Exception as e:
            print(f"Error with get_entry_row: {e}")
            traceback.print_exc()