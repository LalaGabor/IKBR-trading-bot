import pytest
from unittest.mock import MagicMock, patch
import realtime_data_manager_dir


# MagicMock constructor function
@pytest.fixture
def bot_mock():
    return MagicMock()


# Create mock DatabaseManager fixture object
@pytest.fixture
def realtime_data(bot_mock):
    return realtime_data_manager_dir.RealtimeDataManager(bot_mock)
# Reminder, the mock object is callable like a variable. Although it appears we are defining a function above,
# the pytest.fixture decorator will in fact transform the function into a variable-like object called
# realtime_data, which is a mocked RealtimeDataManager class fixture object


# Test case to ensure that the function handles exceptions from handle_realtime_bars
def test_exception_raised_for_handle_realtime_bars(realtime_data):
    # Create a MagicMock object for the bar & symbol argument
    mock_bar = MagicMock()
    mock_symbol = MagicMock()

    # Learning: patch temporarily replaces the mocked object, so that any alterations for testing purposes....
    # .... are temporary.
    # Mock the handle_realtime_bars method to raise an exception, to ensure exceptions are being raised
    with patch.object(realtime_data, "handle_realtime_bars") as mock_process_handle_realtime_bars:
        mock_process_handle_realtime_bars.side_effect = Exception("Simulated Exception")

        # Call the function being tested
        with pytest.raises(Exception) as exception_info:
            realtime_data.handle_realtime_bars(bar=mock_bar, symbol = mock_symbol)

        assert str(exception_info.value) == "Simulated Exception"


#----------------------

from unittest.mock import MagicMock, patch
import pytest
from unittest.mock import MagicMock
import historical_data_manager_dir
from testing.sample_data_manager import sample_empty_dataframe, sample_dataframe


class Bar:
    def __init__(self, open_price, high_price, low_price, close_price, volume, date):
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price
        self.volume = volume
        self.date = date


@pytest.fixture  # Use decorator function to turn following function definition into an argument
def realtime_data_manager_factory():
    def _realtime_data_manager(sample_data):
        bot_mock = MagicMock()  # create magic mock object
        symbol = 'symbol'  # Create dummy symbol string
        bot_mock.df_dict = {symbol: sample_data}  # assign dummy data to key inside dictionary
        return realtime_data_manager_dir.RealtimeDataManager(bot_mock)
        # Create and return a mocked DatabaseManager instance
    return _realtime_data_manager


# Integration test for process_historical_bars
def test_process_historical_bars1(historical_data_manager_factory, sample_empty_dataframe):
    historical_data_manager = historical_data_manager_factory(sample_empty_dataframe)
    historical_data_manager.process_historical_bars(bar=MagicMock(), symbol='symbol')
    # If the dataframe is empty the index of the most recent row should be 0
    assert historical_data_manager.bot.df_dict['symbol'].index[-1] == 0  # as new_index is a local variable we must


# Integration test for process_historical_bars
def test_process_historical_bars2(historical_data_manager_factory, sample_dataframe):
    historical_data_manager = historical_data_manager_factory(sample_dataframe)
    historical_data_manager.process_historical_bars(bar=MagicMock(), symbol='symbol')
    # If the dataframe is NOT empty the index of the most recent row should be 1
    assert historical_data_manager.bot.df_dict['symbol'].index[-1] == 1  # as new_index is a local variable we must


# Integration test for process_historical_bars
def test_process_historical_bars3(historical_data_manager_factory, sample_dataframe):
    # Creating a sample Bar object with required values
    sample_bar = Bar(open_price=100.0, high_price=110.0, low_price=90.0, close_price=105.0, volume=1000, date='2024-04-04')

    historical_data_manager = historical_data_manager_factory(sample_dataframe)
    historical_data_manager.process_historical_bars(bar=sample_bar, symbol='symbol')
    # Getting the last row of the DataFrame
    last_row = historical_data_manager.bot.df_dict['symbol'].iloc[-1]

    # Expected data for comparison
    expected_data = {'Open': 100.0,
                     'High': 110.0,
                     'Low': 90.0,
                     'Close': 105.0,
                     'Volume': 1000,
                     'Date': '2024-04-04',
                     'Tick': '2024-04-04',
                     'is_divergence_open_candidate': 0,
                     'paired_divergence_opens_id': 0,
                     'paired_divergence_opens_closing_price': 0,
                     'paired_divergence_opens_rsi': 0,
                     'is_divergence_high': 0,
                     'rsi': 0,
                     'symbol': 'symbol'}

    # Asserting individual elements of the last row
    for key, value in expected_data.items():
        assert last_row[key] == value# Getting the last row of the DataFrame
    last_row = historical_data_manager.bot.df_dict['symbol'].iloc[-1]