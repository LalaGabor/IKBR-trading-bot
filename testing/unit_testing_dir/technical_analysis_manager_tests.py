import pytest
from unittest.mock import MagicMock
from testing.sample_data_manager  import big_sample_dataframe

#Use a factory to pass sample data to a mocked ta manager object
@pytest.fixture  # Use decorator function to turn following function definition into an pytest object
def rsi_calculator_factory():
    def _rsi_calculator(sample_data):
        ##TODO: a mocked bot object is not required, as a it is not required on init? How to pass the data then?
        bot_mock = MagicMock()  # create magic mock object
        symbol = 'symbol'  # Create dummy symbol string
        bot_mock.df_dict = {symbol: sample_data}  # assign dummy data to key inside dictionary
        # Learning, how are we able to access RSICalculator with the below
        # Answer: the __init__.py file exposes the RSICalculator class constructor when one imports the technical_analysis_manager_dir parent directory
        return technical_analysis_manager_dir.RSICalculator(bot_mock)
        # Create and return a mocked TechnicalAnalysisManager instance
    return _technical_analysis_manager
# Def Tests
"""
Test 1: rsi calculator module: test_append_rsi_to_dataframe.
-- Assert that the close column is type float

-- Implementation: ingest large sample dataframe. Assert dataframe['Closes'].type() = float

-- Status: In progress

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

-- Status: Open

Test 3: divergence calculator module: test_get_close_candidates_nearest_open.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_divergence_open_candidate == 1

-- Assert that the values in paired_divergence_opens_id & paired_divergence_opens_closing_price of rows where
is_divergence_open_candidate == 1, match the paired divergence open row

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 4: divergence calculator module: test_limit_divergence_to_accepted_row.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_divergence_open_candidate == 1

-- Assert that the values in paired_divergence_opens_id & paired_divergence_opens_closing_price of rows where
is_divergence_open_candidate == 1, match the paired divergence open row

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 5: divergence calculator module: test_calculate_divergence.
-- Test preparation. Find a row(s) number in the sample big dataframe where the logical conditions to set
is_divergence_high == 1 are met

-- Assert that the value in is_divergence_high of rows where the logical conditions are met, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 6: entry calculator module: test_get_entry_candidates.
-- Test preparation. Find a row(s) number in the sample big dataframe where the logical conditions to set
is_entry_candidate == 1 are met (if last_row['rsi'] >= 65 and last_row['is_divergence_high'] == 1)

-- Assert that the value in is_entry_candidate of rows where the logical conditions are met, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

Test 7: entry calculator module: test_get_entry_row.
-- Test preparation. Find a row(s) number in the sample big dataframe where is_entry_candidate == 1

-- Assert that the value in is_entry_candidate of rows which pass logical checks, == 1

-- Implementation: ingest large sample dataframe. Make assertion using expected row number(s)

-- Status: Open

"""
