Disclaimer: This is an incomplete fork of a private repo.
DO NOT use this repository for trading purposes. Only for review.

Known Limitations:

Security: Hardcoded credentials and potential SQL injection risks.

Error Handling: Silently handled errors and excessive exception handling.

Transactions: Inconsistent transaction handling and insufficient validation.

Testing: Overreliance on unit tests and insufficient end-to-end coverage.

Logging: No logging or execution tracing.

Data Pipeline: Inefficient architecture, with pandas transformations that could be performed in SQL.

Data Integrity: Insufficient validation and duplicate handling.

Order Execution: Insufficient safeguards against duplicate orders and partial failures.

Resilience: Limited retry, timeout, and recovery mechanisms.

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
* MySQL database set up and running

3. Start the application
```shell
python bot.py
```
