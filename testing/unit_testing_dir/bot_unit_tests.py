from unittest.mock import MagicMock, patch
import pytest
from pandas.testing import assert_frame_equal
from bot import Bot
import pandas
from testing.sample_data_manager import sample_empty_dataframe, sample_dataframe


class Bar:
    def __init__(self, open_price, high_price, low_price, close_price, volume, date):
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price
        self.volume = volume
        self.date = date


@pytest.fixture  # Use decorator function to turn following function definition into an "argument" for later tests
def bot_factory():
    def _bot(sample_data):
        bot_mock = MagicMock()  # create magic mock object
        symbol = 'symbol'  # Create dummy symbol string
        bot_mock.df_dict = {symbol: sample_data}  # assign dummy data to key inside dictionary
        return bot.Bot(bot_mock)
        # Create and return a mocked DatabaseManager instance
    return _bot


import pytest
from unittest.mock import MagicMock
import database_manager_dir
import sqlalchemy


# Create mock DatabaseManager object
@pytest.fixture
def database_manager(bot_mock):
    return database_manager_dir.DatabaseManager(bot_mock)


# Test case for the get_mysql_engine method
def test_get_mysql_engine(bot_mock):
    # Create a DatabaseManager instance with the mock Bot
    database_manager = database_manager_dir.DatabaseManager(bot_mock)

    # Call the method being tested
    mysql_engine = database_manager.get_mysql_engine()

    # Assert that the method returned an instance of SQLAlchemy's Engine
    assert isinstance(mysql_engine, sqlalchemy.engine.Engine)

def test_dataframe_creation():
    symbol_list = ["symbol"]
    bot_mock = Bot(symbol_list,create_clients=False)

    expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Date', 'Tick',
                        'is_divergence_open_candidate', 'paired_divergence_opens_id',
                        'paired_divergence_opens_closing_price', 'paired_divergence_opens_rsi',
                        'is_divergence_high', 'rsi', 'is_entry_candidate', 'is_entry', 'symbol']

    expected_df = pandas.DataFrame(columns=expected_columns)

    assert_frame_equal(bot_mock.df_dict['symbol'], expected_df)