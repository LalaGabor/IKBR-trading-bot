import traceback
import pandas
import numpy
from testing.sample_data_manager  import big_sample_dataframe2

pandas.options.mode.chained_assignment = None  # Suppress the SettingWithCopy warning


class DivergenceCalculator:

    # function purpose: does the evaluated row potentially "open" a divergence, by being a local peak
    def get_open_candidate(self, pandas_dataframe, row_number):
        try:
            # check if the pandas data frame has enough rows & the examined row has a sufficient rsi value
            if len(pandas_dataframe) >= 11 and pandas_dataframe['rsi'].iloc[row_number - 5] >= 70:
                # store the evaluated closing price
                evaluated_closing_price = pandas_dataframe.loc[pandas_dataframe.index[row_number - 5], 'Close']

                if not pandas.notna(evaluated_closing_price) or not numpy.isfinite(evaluated_closing_price).all():
                    raise ValueError("Evaluated closing price is not a valid number")

                # check if the evaluated closing price is strictly greater than the closing price of the 5 preceding
                # & 5 succeeding rows
                if all((evaluated_closing_price > pandas_dataframe.loc[pandas_dataframe.index[i], 'Close']).all() for i in
                       range(row_number, row_number - 5, -1)) and all(
                    (evaluated_closing_price > pandas_dataframe.loc[pandas_dataframe.index[i], 'Close']).all() for i in
                    range(row_number - 6, row_number - 11, -1)):
                    # if yes, set divergence candidate open = 1
                    pandas_dataframe.loc[pandas_dataframe.index[row_number - 5], 'is_divergence_open_candidate'] = 1

                else:
                    # if not, set the divergence candidate open = 0
                    pandas_dataframe.loc[pandas_dataframe.index[row_number - 5], 'is_divergence_open_candidate'] = 0
                    return

            pandas_dataframe['is_divergence_open_candidate'] = pandas_dataframe['is_divergence_open_candidate'].astype(
                int)

        except Exception as e:
            print(f"Error in get_open_candidate: {e}")
            traceback.print_exc()

    def get_close_candidates_nearest_open(self, pandas_dataframe, row_number):
        try:
            # Check if the dataframe is empty
            if not pandas_dataframe.empty:

                # If the dataframe is not empty, check if the length of the dataframe is longer than 62 rows (+ row
                # number), & if the last 62 rows (+ row number) contain a row where the
                # 'is_divergence_open_candidate' column is equal to 1
                if len(pandas_dataframe) >= row_number + 62 and (
                        pandas_dataframe.tail(row_number + 62)['is_divergence_open_candidate'] == 1).any():

                    try:
                        # Set divergence_candidates equal to the index of the rows where
                        # 'is_divergence_open_candidate' is 1 (stored as a list of int64 values)
                        divergence_candidates = pandas_dataframe[
                            pandas_dataframe['is_divergence_open_candidate'] == 1].tail(row_number + 62).index

                        # Ensure divergence_candidates is not empty
                        if not divergence_candidates.empty:

                            # Set variable equal to the last value in the divergence_candidates list
                            variable = divergence_candidates[-1]

                            # Set the value in column paired_divergence_opens_id (for the row
                            # pandas_dataframe.index[row_number]) equal to the integer value of 'variable' + 1.
                            pandas_dataframe.loc[pandas_dataframe.index[row_number],'paired_divergence_opens_id'] =  \
                                int(variable + 1)

                            variable3 = pandas_dataframe['Close'].loc[int(variable)]
                            pandas_dataframe.loc[pandas_dataframe.index[row_number],
                                                 'paired_divergence_opens_closing_price'] = int(float(variable3))
                            variable5 = pandas_dataframe['rsi'].loc[int(variable)]
                            pandas_dataframe.loc[
                                pandas_dataframe.index[row_number], 'paired_divergence_opens_rsi'] = int(
                                float(variable5))

                    except IndexError:
                        print("No occurrence with is_divergence_open_candidate == 1 in the last 61 rows")
                    except Exception as e:
                        print(f"Error: {e}")
        except Exception as e:
            print(f"Error in get_close_candidates_nearest_open: {e}")
            traceback.print_exc()

    # Ensures that the 5 rows following a divergence candidate open can not be evaluated as a close (prevent open &
    # closes too close to each other)
    def limit_divergence_to_accepted_row(self, pandas_dataframe, row_number):
        try:
            # Ensure the pandas dataframe is longer than 11 entries
            if len(pandas_dataframe) >= 11:

                # For the selected row or the 5 preceding rows....
                for i in range((-row_number), (-1 * row_number + 6)):

                    # ....Check if 'is_divergence_open_candidate' is 1
                    if pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_divergence_open_candidate'] == 1:

                        # If yes, set 'paired_divergence_opens_id' equal to 0,....
                        pandas_dataframe.loc[pandas_dataframe.index[row_number], 'paired_divergence_opens_id'] = 0
                        # If yes, set 'paired_divergence_opens_closing_price' equal to 0,....
                        pandas_dataframe.loc[pandas_dataframe.index[row_number],
                                             'paired_divergence_opens_closing_price'] = 0
                        # If yes, set 'paired_divergence_opens_rsi' equal to 0,....
                        pandas_dataframe.loc[pandas_dataframe.index[row_number], 'paired_divergence_opens_rsi'] = 0

                        # Learning: Why is the 'break' necessary here?
                        # Answer: The break ensure that the for loop exits, as soon as the if condition is satisfied.
                        # In this case, if a row in the targeted range contains a 'is_divergence_open_candidate'
                        # which is equal to 1.
                        break

        except Exception as e:
            print(f"Error in limit_divergence_to_accepted_row: {e}")
            traceback.print_exc()

    @staticmethod
    def calculate_divergence(pandas_dataframe, row_number):
        try:
            # Check if rsi & paired_divergence_opens_rsi is in the pandas_dataframe argument and that there is at
            # least one non-null entry
            if 'rsi' in pandas_dataframe.columns and not pandas_dataframe['rsi'].isnull().all() and not \
                    pandas_dataframe[
                    'paired_divergence_opens_rsi'].isna().all():

                # Set 'last_row' equal to the targeted row in the pandas dataframe passed to the method
                last_row = pandas_dataframe.iloc[row_number]

                # Check if the last row's 'rsi' value is less than the value in 'paired_divergence_opens_rsi' & that
                # the last row's 'Close' value is greater than the value in 'paired_divergence_opens_closing_price'
                if last_row['rsi'] < last_row['paired_divergence_opens_rsi'] and last_row['Close'] > last_row[
                    'paired_divergence_opens_closing_price']:

                    # If yes, set 'is_divergence_high' equal to 1
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_divergence_high'] = 1

                else:
                    # If not, set 'is_divergence_high' equal to 0
                    pandas_dataframe.loc[pandas_dataframe.index[row_number], 'is_divergence_high'] = 0

                return

        except Exception as e:
            print(f"Error in calculate_divergence: {e}")
            traceback.print_exc()
