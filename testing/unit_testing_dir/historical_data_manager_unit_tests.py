import pytest
from unittest.mock import MagicMock, patch
import historical_data_manager_dir
# Import the sample_bar function from sample_data.py
from testing.sample_data import sample_bar, sample_dataframe, sample_symbol_dictionary
import pandas


# Create a sample Bar object containing dummy data
sample_bar = sample_bar()
sample_symbol_dictionary = sample_symbol_dictionary()

# MagicMock constructor function
@pytest.fixture
def bot_mock():
    return MagicMock()


# Create mock DatabaseManager fixture object
@pytest.fixture
def historical_data(bot_mock):
    return historical_data_manager_dir.HistoricalDataManager(bot_mock)
# Reminder, the mock object is callable like a variable. Although it appears we are defining a function above,
# the pytest.fixture decorator will in fact transform the function into a variable-like object called
# historical_data, which is a mocked HistoricalDataManager class fixture object


# Test case to ensure that the function handles exceptions from process_historical_bars
def test_process_historical_bars_exception_raising(historical_data):
    # Create a MagicMock object for the bar argument
    mock_bar = MagicMock()

    # Learning: patch temporarily replaces the mocked object, so that any alterations for testing purposes....
    # .... are temporary.
    # Mock the process_historical_bars method to raise an exception, to ensure exceptions are being raised
    with patch.object(historical_data, "process_historical_bars") as mock_process_historical_bars:
        mock_process_historical_bars.side_effect = Exception("Simulated Exception")

        # Call the function being tested
        with pytest.raises(Exception) as exception_info:
            historical_data.incoming_historical_data(reqID=1, bar=mock_bar)

        assert str(exception_info.value) == "Simulated Exception"


