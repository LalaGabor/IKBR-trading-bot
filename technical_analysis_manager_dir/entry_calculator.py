import pandas
import traceback
pandas.options.mode.chained_assignment = None  # Suppress the SettingWithCopy warning

class EntryCalculator:

    # Find rows which meet the entry conditions
    def get_entry_candidates(self, pandas_dataframe, row_number):
        try:
            # Check that the dataframe is not empty
            if not pandas_dataframe.empty:

                # Set 'last_row' equal to the target row in the dataframe passed to the method
                last_row = pandas_dataframe.iloc[row_number]

                # Check that the 'rsi' value is >= 65 & that the 'is_divergence_high' value is equal to 1, ...
                # ...in last_row
                if last_row['rsi'] >= 65 and last_row['is_divergence_high'] == 1:

                    # If yes, set 'is_entry_candidate' equal to 1
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry_candidate'] = 1

                else:
                    # If not, set 'is_entry_candidate' equal to 0
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry_candidate'] = 0

        except Exception as e:
            print(f"Error with get_entry_candidates realtime data: {e}")
            traceback.print_exc()

    # Find rows which are accepted entries
    def get_entry_row(self, pandas_dataframe, row_number):
        try:
            # Check that the dataframe is not empty and contains the 'is_entry_candidate' column
            if 'is_entry_candidate' in pandas_dataframe.columns and not pandas_dataframe.empty:

                # Check if any of the 5 rows preceding the target row have 'is_entry_candidate' equal to 1
                if pandas_dataframe.loc[pandas_dataframe.index[row_number - 5:row_number], 'is_entry_candidate'] \
                        .eq(1).any():

                    # If yes, set 'is_entry' equal to 0
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry'] = 0

                # Else, check if the targeted row has 'is_entry_candidate' equal to 1
                elif pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry_candidate'] == 1:
                    print(pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry_candidate'])
                    # If yes, set 'is_entry' equal to 1
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry'] = 1

                # Else the target row is not an entry
                else:
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_entry'] = 0

        except Exception as e:
            print(f"Error with get_entry_row: {e}")
            traceback.print_exc()