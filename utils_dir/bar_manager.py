class Bar:
    first_historical_bar = True
    def __init__(self, open_, high, low, close, volume, date, tick):
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        if Bar.first_historical_bar:
            self.date = datetime.now()
            Bar.first_historical_bar = False
        else:
            self.date = date
        self.tick = tick
