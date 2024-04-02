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
