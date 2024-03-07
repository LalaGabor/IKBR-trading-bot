import pandas

pandas.options.mode.chained_assignment = None  # Suppress the SettingWithCopy warning

class EntryCalculator:

    # Find rows which meet the entry conditions
    def get_entry_candidates(self, pandas_dataframe, row_number):
        """print("pd before logic")
        print(pandas_dataframe)
        print(pandas_dataframe.iloc[-1])"""
        # Assuming 'Date' column is in datetime format
        if not pandas_dataframe.empty:
            last_row = pandas_dataframe.iloc[row_number]
            if last_row['rsi'] >= 65 and last_row['is_divergence_high'] == 1:
                pandas_dataframe['is_entry_candidate'].iloc[row_number] = 1
            else:
                pandas_dataframe['is_entry_candidate'].iloc[row_number] = 0
        """print("pd after logic")
        print(pandas_dataframe)
        print(pandas_dataframe.iloc[-1])"""

    # Find rows which are accepted entries
    def get_entry_row(self, pandas_dataframe, row_number):
        if not pandas_dataframe.empty:
            # Assuming 'Date' column is in datetime format
            last_row = pandas_dataframe.iloc[row_number]
            if 'is_entry_candidate' in pandas_dataframe.columns:
                entry_candidates = pandas_dataframe['is_entry_candidate']
                if entry_candidates.iloc[row_number - 5:row_number].eq(1).any():
                    pandas_dataframe['is_entry'].iloc[row_number] = 0
                elif pandas_dataframe['is_entry_candidate'].iloc[row_number] == 1:
                    pandas_dataframe['is_entry'].iloc[row_number] = 1
                    print(f"Entered a trade at {pandas_dataframe.loc[row_number, 'Date']}")
                else:
                    pandas_dataframe['is_entry'].iloc[row_number] = 0
