import pandas
import pytest
import os
import csv
from datetime import datetime


class Bar:
    def __init__(self, open_, high, low, close, volume, date, tick):
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.date = date
        self.tick = tick


def sample_bar():
    mock_bar = Bar(100, 110, 90, 105, 1000, "2024-03-25", "2024-03-25")
    return mock_bar


# Empty Dataframe
@pytest.fixture
def sample_empty_dataframe():
    no_data = pandas.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Date', 'Tick',
                                                        'is_divergence_open_candidate', 'paired_divergence_opens_id',
                                                        'paired_divergence_opens_closing_price', 'paired_divergence_opens_rsi',
                                                        'is_divergence_high', 'rsi', 'symbol'])
    return no_data


@pytest.fixture
def sample_dataframe():
    sample = pandas.DataFrame({'Open': [100],
                'High': [110],
                'Low': [90],
                'Close': [105],
                'Volume': [1000],
                'Date': ["2024-03-25"],
                'Tick': ["2024-03-25"],
                'is_divergence_open_candidate': [0],
                'paired_divergence_opens_id': [0],
                'paired_divergence_opens_closing_price': [0],
                'paired_divergence_opens_rsi': [0],
                'is_divergence_high': [0],
                'rsi': [0],
                'is_entry_candidate': [0],
                'is_entry': [0],
                'symbol': ["symbol"]})

    # Convert 'Date' column to datetime format
    sample['Date'] = pandas.to_datetime(sample['Date'])

    # Convert 'Tick' column to datetime format
    sample['Tick'] = pandas.to_datetime(sample['Tick'])


    return sample

def sample_dataframe_query(symbol):
    sample_query = f"""CREATE TABLE IF NOT EXISTS bot_{symbol}_debug (
            Open FLOAT,
            High FLOAT,
            Low FLOAT,
            Close FLOAT,
            Volume INT,
            Date DATE,
            is_divergence_open_candidate INT,
            paired_divergence_opens_id INT,
            paired_divergence_opens_closing_price FLOAT,
            paired_divergence_opens_rsi FLOAT,
            is_divergence_high INT,
            rsi FLOAT,
            is_entry_candidate INT,
            is_entry INT,
            symbol VARCHAR(50)
        )"""
    return sample_query


def sample_symbol_dictionary():

    sample_symbol_dict  = {1: "AAPL", 2: "GOOG"}

    return sample_symbol_dict


@pytest.fixture
def sample_date_data():

    sample_dates = {'Date': pandas.to_datetime(['2022-01-02 00:00:00', '2022-01-01 00:00:00'])}
    dataframe = pandas.DataFrame(sample_dates)
    return dataframe

@pytest.fixture
def big_sample_dataframe():
    csv_file = os.path.join(os.path.dirname(__file__), 'sample_csv_data.csv')
    parse_dates = ['Date']
    big_sample = pandas.read_csv(csv_file, delimiter=',', encoding='utf-8', quoting=csv.QUOTE_NONE,
                                 parse_dates=parse_dates)
    big_sample['Tick'] = big_sample['Date']
    return big_sample

"""
---------------------------------
"""
## For Debugging Divergence Calculator...REMOVE ME
def big_sample_dataframe2():
    csv_file = os.path.join(os.path.dirname(__file__), 'sample_csv_data.csv')
    parse_dates = ['Date']
    big_sample = pandas.read_csv(csv_file, delimiter=',', encoding='utf-8', quoting=csv.QUOTE_NONE,
                                 parse_dates=parse_dates)
    big_sample['Tick'] = big_sample['Date']
    return big_sample