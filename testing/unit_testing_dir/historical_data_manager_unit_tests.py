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
def historical_data_manager_factory():
    def _historical_data_manager(sample_data):
        bot_mock = MagicMock()  # create magic mock object
        symbol = 'symbol'  # Create dummy symbol string
        bot_mock.df_dict = {symbol: sample_data}  # assign dummy data to key inside dictionary
        return historical_data_manager_dir.HistoricalDataManager(bot_mock)
        # Create and return a mocked DatabaseManager instance
    return _historical_data_manager


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

