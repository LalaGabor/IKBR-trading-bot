# IKBR-trading-bot
Trading bot places orders, based on symbols, timeframe &amp; strategies

#### Setting up the project

1. Initialize the virtual environment
```shell
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
```

2. Ensure the required applications are installed and configured
* TWS Application and an IBKR account with the API enabled
* MySQL database set up and running **#TODO consider Docker**

3. Start the application
```shell
python bot.py
```
