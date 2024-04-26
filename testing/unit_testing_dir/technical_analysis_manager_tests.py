import pytest
from unittest.mock import MagicMock
import technical_analysis_manager_dir
from bot import Bot
from testing.sample_data_manager  import big_sample_dataframe


# Test the capability of the 'append_rsi_to_dataframe' method (of the RSICalculator class constructor) to correctly
# calculate the rsi of a target row
def test_append_rsi_to_dataframe(big_sample_dataframe):

    target_date = '2024-03-18 11:24:00.000'  # This is the date of the row whose rsi value is being evaluated
    bottom_range_target_rsi = 44.381  # This is the rsi of the row whose rsi value is being evaluated
    top_range_target_rsi = 44.382

    # Learning: Here the 'spec=' keyword informs the MagicMock class constructor which object is being mocked. It
    # therefore defines which methods and attributes that the mocked object should have.
    mocked_rsi_calculator = MagicMock(spec=technical_analysis_manager_dir.RSICalculator)

    # Create a sample dataframe via big_sample_dataframe
    symbol = 'symbol'
    sample_data = {symbol: big_sample_dataframe}
    # Call the append_rsi_to_dataframe method
    mocked_rsi_calculator.append_rsi_to_dataframe(sample_data)
    # Select the row which contains the target date (for later test assertion)
    filtered_df = sample_data['symbol'].loc[sample_data['symbol']['Date'] == target_date]

    assert bottom_range_target_rsi < filtered_df['rsi'].iloc[0] < top_range_target_rsi


def test_get_open_candidate(big_sample_dataframe):

    target_date = '2024-03-18 12:54:00.000'  # This is the date of the row whose divergence open value is being
    # evaluated

    # Learning: Here the 'spec=' keyword informs the MagicMock class constructor which object is being mocked. It
    # therefore defines which methods and attributes that the mocked object should have.
    mocked_divergence_calculator = MagicMock(spec=technical_analysis_manager_dir.DivergenceCalculator)

    # Create a sample dataframe via big_sample_dataframe
    symbol = 'symbol'
    sample_data = {symbol: big_sample_dataframe}

    # Call the get_open_candidate method
    mocked_divergence_calculator.get_open_candidate(sample_data, row_number=-1)

    # Select the row which contains the target date (for later test assertion)
    filtered_df = sample_data['symbol'].loc[sample_data['symbol']['Date'] == target_date]

    assert filtered_df['is_divergence_open_candidate'].iloc[0] == 0


def test_get_close_candidates_nearest_open(big_sample_dataframe):

    update_date = '2024-03-18 12:54:00.000'  # This is the date of the row whose divergence open value is being
    # updated, to ensure later rows will have a pair

    evaluation_date = '2024-03-18 13:26:00.000'  # This is the date of the row whose divergence open value is being
    # evaluated

    # Create a sample dataframe via big_sample_dataframe
    symbol = 'symbol'
    sample_data = {symbol: big_sample_dataframe}

    # Set the 'is_divergence_open_candidate' value == 1, at the update date
    # Learning: What is the syntax to access a pandas dataframe row+column value?
    # Answer: First select the dataframe, for this use case it is: sample_data['symbol']. Next call the loc method
    # with: .loc[] (label based indexing). Inside the .loc[] property, specify a row and column label. Note: in the
    # use case below, we conditionally select the row where the ['Date']  == update_date
    sample_data['symbol'].loc[sample_data['symbol']['Date'] == update_date, 'is_divergence_open_candidate'] = 1

    print(sample_data['symbol'].loc[sample_data['symbol']['Date'] == update_date, 'is_divergence_open_candidate'])

    # Create an instance of DivergenceCalculator
    divergence_calculator_instance = technical_analysis_manager_dir.DivergenceCalculator()

    # Call the get_close_candidates_nearest_open
    divergence_calculator_instance.get_close_candidates_nearest_open(sample_data['symbol'], row_number=-1)


    """
    --------------------
    # Learning: Here the 'spec=' keyword informs the MagicMock class constructor which object is being mocked. It
    # therefore defines which methods and attributes that the mocked object should have.
    mocked_divergence_calculator = MagicMock(spec=technical_analysis_manager_dir.DivergenceCalculator)

    # Configure the return value of the mocked method
    mocked_divergence_calculator.get_close_candidates_nearest_open.return_value = sample_data['symbol']

    # Call the get_open_candidate method
    mocked_divergence_calculator.get_close_candidates_nearest_open(sample_data, row_number=-1)
    ----------------------
    """


    print(sample_data['symbol'].loc[sample_data['symbol']['Date']== update_date, 'is_divergence_open_candidate'])
    # Select the row which contains the target date (for later test assertion)
    evaluation_df = sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date]
    print(evaluation_df)
    print(evaluation_df['paired_divergence_opens_id'].iloc[-1])
    # Learning: Why do I need to specify [0] in the below iloc call (integer based indexing)
    # Answer: Every call of the '.iloc' property requires an integer to specify the row and then column. Example
    # syntax: df.iloc[1, 0] will access the second [1] row, of the first [0] column. In the below use case we specify
    # the column by label, so we only need to specify the row by integer, i.e. [0]
    assert evaluation_df['paired_divergence_opens_id'].iloc[-1] == 128


def test_limit_divergence_to_accepted_row(big_sample_dataframe):

    update_date = '2024-03-18 12:54:00.000'  # This is the date of the row whose divergence open value is being
    # updated, to ensure later rows will have a pair

    evaluation_date = '2024-03-18 12:55:00.000'  # This is the date of the row whose divergence open value is being
    # evaluated

    # Create a sample dataframe via big_sample_dataframe
    symbol = 'symbol'
    sample_data = {symbol: big_sample_dataframe}

    # Set the 'is_divergence_open_candidate' value == 1, at the update date
    sample_data['symbol'].loc[sample_data['symbol']['Date'] == update_date, 'is_divergence_open_candidate'] = 1

    # Create an instance of DivergenceCalculator
    divergence_calculator_instance = technical_analysis_manager_dir.DivergenceCalculator()

    # Learning: How to find the row number of the targeted evaluation_date's row, based on update_date?
    # Answer: We find the row number of the update_date's row and add 1. Using '.index' returns an index object. By
    # converting the index object to a list with '.tolist()' we make the contents of the object available. Then
    # select the first item in the list with [0] and convert the value to an integer with 'int()'. Afterwards add 1
    # as the 'Date' data increments by 1 minute, which is the delta from update_date to evaluation_date
    evaluation_row = int(sample_data['symbol'][sample_data['symbol']['Date'] == update_date].index.tolist()[0]) + 1

    # Call the limit_divergence_to_accepted_row method
    divergence_calculator_instance.limit_divergence_to_accepted_row(sample_data['symbol'], row_number=evaluation_row)

    # Define the evaluation dataframe using the evaluation_date
    evaluation_df = sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date]

    # Assert the last row entry in the column 'paired_divergence_opens_id' of the evaluation dataframe is equal to 0
    assert evaluation_df['paired_divergence_opens_id'].iloc[-1] == 0


def test_calculate_divergence(big_sample_dataframe):

    evaluation_date = '2024-03-18 13:26:00.000'  # This is the date of the row whose divergence open value is being
    # evaluated

    # Create a sample dataframe via big_sample_dataframe
    symbol = 'symbol'
    sample_data = {symbol: big_sample_dataframe}

    # Set the 'paired_divergence_opens_rsi' value == 99.99 ...
    # ...(to force it larger than the value in the rsi column (max 100))
    sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date, 'paired_divergence_opens_rsi'] = 99.99

    # Set the 'paired_divergence_opens_closing_price' value == 00.01 ...
    # ...(to force it larger than the value in the rsi column (min 0))
    sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date,
                              'paired_divergence_opens_closing_price'] = 00.01

    # Create an instance of DivergenceCalculator
    divergence_calculator_instance = technical_analysis_manager_dir.DivergenceCalculator()

    # Get the row_number of the evaluation date in the dataframe
    evaluation_row = int(sample_data['symbol'][sample_data['symbol']['Date'] == evaluation_date].index.tolist()[0])

    # Call the calculate_divergence method
    divergence_calculator_instance.calculate_divergence(sample_data['symbol'], row_number=evaluation_row)

    # Define the evaluation dataframe using the evaluation_date
    evaluation_df = sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date]

    # Assert the last row entry in the column 'is_divergence_high' of the evaluation dataframe is equal to 1
    assert evaluation_df['is_divergence_high'].iloc[-1] == 1


def test_get_entry_candidates(big_sample_dataframe):

    evaluation_date = '2024-03-18 13:26:00.000'  # This is the date of the row whose 'is_entry_candidate' is being
    # evaluated

    # Create a sample dataframe via big_sample_dataframe
    symbol = 'symbol'
    sample_data = {symbol: big_sample_dataframe}

    # Set the 'rsi' value == 90 ...
    # ...(to force it larger than 65, to pass the logic check)
    sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date, 'rsi'] = 90

    # Set the 'is_divergence_high' value = 1 ...
    # ...(to force it to pass the logic check)
    sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date,
                              'is_divergence_high'] = 1

    # Create an instance of DivergenceCalculator
    divergence_calculator_instance = technical_analysis_manager_dir.EntryCalculator()

    # Get the row_number of the evaluation date in the dataframe
    evaluation_row = int(sample_data['symbol'][sample_data['symbol']['Date'] == evaluation_date].index.tolist()[0])

    # Call the calculate_divergence method
    divergence_calculator_instance.get_entry_candidates(sample_data['symbol'], row_number=evaluation_row)

    # Define the evaluation dataframe using the evaluation_date
    evaluation_df = sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date]

    # Assert the last row entry in the column 'is_divergence_high' of the evaluation dataframe is equal to 1
    assert evaluation_df['is_entry_candidate'].iloc[-1] == 1


def test_get_entry_row(big_sample_dataframe):

    evaluation_date = '2024-03-18 13:26:00.000'  # This is the date of the row whose 'is_entry' is being evaluated

    update_date = '2024-03-18 13:10:00.000'  # This is the second date of the row whose 'is_entry' is being
    # evaluated

    # Create a sample dataframe via big_sample_dataframe
    symbol = 'symbol'
    sample_data = {symbol: big_sample_dataframe}

    # Set the 'is_entry_candidate' value = 1, for the 'evaluation_date'...
    # ...(to force the call with 'evaluation_date' to pass the first logic check)
    sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date, 'is_entry_candidate'] = 1

    # Set the 'is_entry_candidate' value = 1, for the 'evaluation_date2'...
    # ...(to force the call with 'evaluation_date2' to fail the first logic check)
    sample_data['symbol'].loc[sample_data['symbol']['Date'] == update_date,
                              'is_entry_candidate'] = 1

    # Create an instance of DivergenceCalculator
    divergence_calculator_instance = technical_analysis_manager_dir.EntryCalculator()

    # Get the row_number of the evaluation date in the dataframe (Check that logic passes)
    # Note: the sample dataframe contains 160 rows, to arrive at the correct negative index value (for later iloc
    # processing), the following formula is required.
    #TODO: Remove 'magic' number 160 by storing in variable in sample_data_manager
    evaluation_row = -1 * (160 - int(sample_data['symbol'][sample_data['symbol']['Date'] ==
                                                        evaluation_date].index.tolist()[0]))

    # Set the evaluation row equal to a row following the update_date row
    evaluation_row2 = -1 * (160 +1 - int(sample_data['symbol'][sample_data['symbol']['Date'] ==
                                                        update_date].index.tolist()[0]))

    # Call the calculate_divergence method with evaluation_row
    divergence_calculator_instance.get_entry_row(sample_data['symbol'], row_number=evaluation_row)

    # Call the calculate_divergence method with evaluation_row2
    divergence_calculator_instance.get_entry_row(sample_data['symbol'], row_number=evaluation_row2)

    # Define the evaluation dataframe using the evaluation_date
    evaluation_df = sample_data['symbol'].loc[sample_data['symbol']['Date'] == evaluation_date]

    # Define the evaluation dataframe using the evaluation_date2
    evaluation_df2 = sample_data['symbol'].loc[sample_data['symbol']['Date'] == update_date]

    # Assert the value in the column 'is_entry' of the evaluation dataframe is equal to 1
    assert evaluation_df['is_entry'].iloc[-1] == 1
    # Assert the value in the column 'is_entry' of the evaluation2 dataframe is NOT equal to 1
    assert not evaluation_df2['is_entry'].iloc[-1] == 1


# Def Tests
"""
Test 1: rsi calculator module: test_append_rsi_to_dataframe.
-- Assert that the close column is type float

-- Implementation: ingest large sample dataframe. Assert dataframe['Closes'].type() = float

-- Status: Done

def test_append_rsi_to_dataframe(technical_analysis_manager_factory, big_sample_dataframe):
  store some sample dataframe as a variable
  run the mock ta manager using the sample dataframe as its argument
  assert the variable (sample dataframe) rows rsi == some value
  
  technical_analysis_manager = technical_analysis_manager_factory(big_sample_dataframe)

  
  

Test 2: divergence calculator module: test_get_open_candidate.
-- Test preparation. Find a row number in the sample big dataframe that fulfills the logical checks in the
conditional of get_open_candidate

-- Assert that is_divergence_open_candidate at row_number == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Done

Test 3: divergence calculator module: test_get_close_candidates_nearest_open.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_divergence_open_candidate == 1

-- Assert that the values in paired_divergence_opens_id & paired_divergence_opens_closing_price of rows where
is_divergence_open_candidate == 1, match the paired divergence open row

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Done

Test 4: divergence calculator module: test_limit_divergence_to_accepted_row.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_divergence_open_candidate == 1

-- Assert that the values in paired_divergence_opens_id & paired_divergence_opens_closing_price of rows where
is_divergence_open_candidate == 1, match the paired divergence open row

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Done

Test 5: divergence calculator module: test_calculate_divergence.
-- Test preparation. Find a row(s) number in the sample big dataframe where the logical conditions to set
is_divergence_high == 1 are met

-- Assert that the value in is_divergence_high of rows where the logical conditions are met, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Done

Test 6: entry calculator module: test_get_entry_candidates.
-- Test preparation. Find a row(s) number in the sample big dataframe where the logical conditions to set
is_entry_candidate == 1 are met (if last_row['rsi'] >= 65 and last_row['is_divergence_high'] == 1)

-- Assert that the value in is_entry_candidate of rows where the logical conditions are met, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Done

Test 7: entry calculator module: test_get_entry_row.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_entry_candidate == 1

-- Assert that the value in is_entry_candidate of rows which pass logical checks, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: In progress

"""
