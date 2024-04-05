import pytest
from unittest.mock import MagicMock, patch
import realtime_data_manager_dir
from testing.sample_data_manager import big_sample_dataframe


class Bar:
    def __init__(self, open_price, high_price, low_price, close_price, volume, date):
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price
        self.volume = volume
        self.date = date
        self.tick = date


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

@pytest.fixture  # Use decorator function to turn following function definition into an argument
def realtime_data_manager_factory():
    def _realtime_data_manager(sample_data):
        bot_mock = MagicMock()  # create magic mock object
        symbol = 'symbol'  # Create dummy symbol string
        bot_mock.df_dict = {symbol: sample_data}  # assign dummy data to key inside dictionary
        return realtime_data_manager_dir.RealtimeDataManager(bot_mock)
        # Create and return a mocked DatabaseManager instance
    return _realtime_data_manager


# Test the behaviour of process_realtime_bars when receiving incoming tick data for a date that already exists in
# the respective dataframe
def test_process_realtime_bars_for_existing_date(realtime_data_manager_factory, big_sample_dataframe):

    target_date = '2024-03-18 13:25:00.000'
    sample_bar = Bar(open_price=100.0, high_price=110.0, low_price=90.0, close_price=105.0, volume=1000, date=target_date)

    realtime_data_manager = realtime_data_manager_factory(big_sample_dataframe)

    realtime_data_manager.process_realtime_bars(bar=sample_bar, symbol='symbol')

    # Check the high of the row related to the target date
    filtered_df = realtime_data_manager.bot.df_dict['symbol'].loc[realtime_data_manager.bot.df_dict['symbol']['Date'] == target_date]
    assert filtered_df['High'].iloc[0] == 110.0


# Check that the process_realtime_bars method correctly appends a new row to the dataframe by reviewing the open price
def test_process_realtime_bars_no_existing_date(realtime_data_manager_factory, big_sample_dataframe):

    target_date = '2024-03-18 13:28:00.000'
    sample_bar = Bar(open_price=100.0, high_price=110.0, low_price=90.0, close_price=105.0, volume=1000, date=target_date)

    realtime_data_manager = realtime_data_manager_factory(big_sample_dataframe)

    realtime_data_manager.process_realtime_bars(bar=sample_bar, symbol='symbol')

    # Check the high of the row related to the target date
    filtered_df = realtime_data_manager.bot.df_dict['symbol'].loc[realtime_data_manager.bot.df_dict['symbol']['Date'] == target_date]
    assert filtered_df['Open'].iloc[0] == 100.0
