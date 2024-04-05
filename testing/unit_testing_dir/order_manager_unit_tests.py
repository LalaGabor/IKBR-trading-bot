import pytest
from unittest.mock import MagicMock, patch
import os
import order_manager_dir
from testing.sample_data_manager import sample_dataframe


class Bar:
    def __init__(self, open_price, high_price, low_price, close_price, volume, date):
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price
        self.volume = volume
        self.date = date
        self.tick = date


@pytest.fixture  # Use decorator function to turn following function definition into an argument
def order_manager_factory():
    def _order_manager(sample_data):
        bot_mock = MagicMock()  # create magic mock object
        symbol = 'symbol'  # Create dummy symbol string
        bot_mock.df_dict = {symbol: sample_data}  # assign dummy data to key inside dictionary
        bot_mock.order_id = 1
        return order_manager_dir.OrderManager(bot_mock)
        # Create and return a mocked DatabaseManager instance
    return _order_manager


# Test the behaviour of calculate_stop_loss when receiving incoming tick data
def test_calculate_stop_loss(order_manager_factory, sample_dataframe):

    target_date = '2024-03-18 13:25:00.000'
    sample_bar = Bar(open_price=100.0, high_price=110.0, low_price=90.0, close_price=105.0, volume=1000, date=target_date)

    order_manager = order_manager_factory(sample_dataframe)

    stop_loss_test = order_manager.calculate_stop_loss(bar_close=sample_bar.close)

    # Check the high of the row related to the target date
    assert stop_loss_test == 105*0.99


# Test the behaviour of calculate_profit_target when receiving incoming tick data
def test_calculate_profit_target(order_manager_factory, sample_dataframe):

    target_date = '2024-03-18 13:25:00.000'
    sample_bar = Bar(open_price=100.0, high_price=110.0, low_price=90.0, close_price=105.0, volume=1000, date=target_date)

    order_manager = order_manager_factory(sample_dataframe)

    stop_loss_test = order_manager.calculate_stop_loss(bar_close=sample_bar.close)

    # Check the high of the row related to the target date
    assert stop_loss_test == 105*0.99


# Test the behaviour of order_id iteration when calling place_order_if_entry_conditions_met
def test_place_order_if_entry_conditions_met(order_manager_factory, sample_dataframe):

    target_date = '2024-03-18 13:25:00.000'
    sample_bar = Bar(open_price=100.0, high_price=110.0, low_price=90.0, close_price=105.0, volume=1000, date=target_date)

    order_manager = order_manager_factory(sample_dataframe)

    # Check the high of the row related to the target date
    assert order_manager.orderId == 4


def test_load_order_id_file_not_found(order_manager_factory, tmp_path, sample_dataframe):
    order_manager = order_manager_factory(sample_dataframe)
    # Test if FileNotFoundError is raised when file does not exist
    with pytest.raises(FileNotFoundError):
        order_manager.load_order_id()

def test_load_order_id_correct_format(order_manager_factory, tmp_path, sample_dataframe):
    order_manager = order_manager_factory(sample_dataframe)
    # Test if order_id is loaded correctly from the file
    data = "2024-04-05 12345"
    file_path = tmp_path / "order_id.txt"
    with open(file_path, "w") as file:
        file.write(data)

    order_manager.load_order_id()
    assert order_manager.orderId == 12345

def test_load_order_id_incorrect_format(order_manager_factory, tmp_path, sample_dataframe):
    order_manager = order_manager_factory(sample_dataframe)
    # Test if ValueError is raised when file has incorrect format
    data = "2024-04-05"
    file_path = tmp_path / "order_id.txt"
    with open(file_path, "w") as file:
        file.write(data)

    with pytest.raises(ValueError):
        order_manager.load_order_id()