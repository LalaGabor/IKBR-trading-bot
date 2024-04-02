import pandas


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


# Note: Dependent tests will expect this to contain only one row
def sample_dataframe():
    sample = pandas.DataFrame({'Open': 100,
                'High': 110,
                'Low': 90,
                'Close': 105,
                'Volume': 1000,
                'Date': "2024-03-25",
                'Tick': "2024-03-25",
                'is_divergence_open_candidate': 0,
                'paired_divergence_opens_id': 0,
                'paired_divergence_opens_closing_price': 0,
                'paired_divergence_opens_rsi': 0,
                'is_divergence_high': 0,
                'rsi': 0,
                'symbol': "AAPL"})
    return sample


def sample_symbol_dictionary():

    sample_symbol_dict  = {1: "AAPL", 2: "GOOG"}

    return sample_symbol_dict
