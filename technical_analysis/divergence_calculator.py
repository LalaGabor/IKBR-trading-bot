import traceback

class DivergenceCalculator:

    # function purpose: does the evaluated row potentially "open" a divergence, by being a local peak
    @staticmethod
    def get_open_candidate(pandas_dataframe, row_number):
        try:
            # check if the pandas data frame has enough rows & the examined row has a sufficient rsi value
            if len(pandas_dataframe) >= 11 and pandas_dataframe['rsi'].iloc[row_number - 5] >= 70:
                # store the evaluated closing price
                evaluated_closing_price = pandas_dataframe['Close'].iloc[row_number - 5]
                # check if the evaluated closing price is strictly greater than the closing price of the 5 preceding
                # & 5 succeeding rows
                if all((evaluated_closing_price > pandas_dataframe['Close'].iloc[i]).all() for i in
                       range(row_number, row_number - 5, -1)) and all(
                    (evaluated_closing_price > pandas_dataframe['Close'].iloc[i]).all() for i in
                    range(row_number - 6, row_number - 11, -1)):
                    # if yes, set divergence candidate open = 1
                    pandas_dataframe['is_divergence_open_candidate'].iloc[row_number - 5] = 1
                else:
                    # if not, set the divergence candidate open = 0
                    pandas_dataframe['is_divergence_open_candidate'].iloc[row_number - 5] = 0
                    return

            pandas_dataframe['is_divergence_open_candidate'] = pandas_dataframe['is_divergence_open_candidate'].astype(
                int)
        except Exception as e:
            print(f"Error in get_open_candidate: {e}")
            traceback.print_exc()

    def get_close_candidates_nearest_open(self, pandas_dataframe, row_number):
        try:
            if not pandas_dataframe.empty:
                if len(pandas_dataframe) >= row_number + 62 and (
                        pandas_dataframe.tail(row_number + 62)['is_divergence_open_candidate'] == 1).any():
                    try:
                        # Find the index of the first occurrence where 'is_divergence_open_candidate' is 1
                        divergence_candidates = pandas_dataframe[
                            pandas_dataframe['is_divergence_open_candidate'] == 1].tail(row_number + 62).index
                        if not divergence_candidates.empty:
                            variable = divergence_candidates[-1]
                            variable2 = int(variable)
                            pandas_dataframe['paired_divergence_opens_id'].iloc[row_number] = variable2 + 1
                            variable3 = pandas_dataframe['Close'].loc[variable2]
                            variable4 = float(variable3)
                            pandas_dataframe['paired_divergence_opens_closing_price'].iloc[row_number] = variable4
                            variable5 = pandas_dataframe['rsi'].loc[variable2]
                            variable6 = float(variable5)
                            pandas_dataframe['paired_divergence_opens_rsi'].iloc[row_number] = variable6
                    except IndexError:
                        print("No occurrence with is_divergence_open_candidate == 1 in the last 61 rows")
                    except Exception as e:
                        print(f"Error: {e}")
        except Exception as e:
            traceback.print_exc()

    def limit_divergence_to_accepted_row(self, pandas_dataframe, row_number):
        try:
            if len(pandas_dataframe) >= 11:
                # Check if 'is_divergence_open_candidate' is 1 in the current row or the previous 5 rows
                for i in range((-row_number), (-1 * row_number + 6)):
                    if pandas_dataframe['is_divergence_open_candidate'].iloc[-i] == 1:
                        pandas_dataframe['paired_divergence_opens_id'].iloc[row_number] = 0
                        pandas_dataframe['paired_divergence_opens_closing_price'].iloc[row_number] = 0
                        pandas_dataframe['paired_divergence_opens_rsi'].iloc[row_number] = 0
                        break
        except Exception as e:
            # Handle specific exceptions if needed
            print(f"Error: {e}")

    @staticmethod
    def calculate_divergence(pandas_dataframe, row_number):
        try:
            if 'rsi' in pandas_dataframe.columns and not pandas_dataframe['rsi'].isnull().all():
                last_row = pandas_dataframe.iloc[row_number]
                if not pandas_dataframe['rsi'].isna().all() and not pandas_dataframe[
                    'paired_divergence_opens_rsi'].isna().all():
                    if last_row['rsi'] < last_row['paired_divergence_opens_rsi'] and last_row['Close'] > last_row[
                        'paired_divergence_opens_closing_price']:
                        pandas_dataframe['is_divergence_high'].iloc[row_number] = 1
                    else:
                        pandas_dataframe['is_divergence_high'].iloc[row_number] = 0
                else:
                    pandas_dataframe['is_divergence_high'].iloc[row_number] = 0

                return

        except Exception as e:
            print(f"Error in calculate_divergence: {e}")
            traceback.print_exc()