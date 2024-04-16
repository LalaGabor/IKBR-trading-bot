from pandas.testing import assert_frame_equal
from bot import Bot
import pandas
from ibapi.contract import Contract



def test_dataframe_creation():
    symbol_list = ["symbol"]
    bot_mock = Bot(symbol_list,create_clients=False)

    expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Date', 'Tick',
                        'is_divergence_open_candidate', 'paired_divergence_opens_id',
                        'paired_divergence_opens_closing_price', 'paired_divergence_opens_rsi',
                        'is_divergence_high', 'rsi', 'is_entry_candidate', 'is_entry', 'symbol']

    expected_df = pandas.DataFrame(columns=expected_columns)

    assert_frame_equal(bot_mock.df_dict['symbol'], expected_df)


def test_get_symbols_contract_object():

    symbol = ["symbol"]

    bot_mock = Bot(symbol,create_clients=False)

    contract = bot_mock.get_symbols_contract_object(symbol)

    assert isinstance(contract, Contract)

    # Check contract attributes
    assert contract.symbol == symbol
    assert contract.secType == "STK"
    assert contract.exchange == "SMART"
    assert contract.currency == "EUR"
