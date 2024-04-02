import pytest
from unittest.mock import MagicMock
import database_manager_dir
import mysql.connector
import pandas
from testing.sample_data import sample_date_data, sample_dataframe, sample_dataframe_query


@pytest.fixture  # This decorator is somewhat 'magical'. Rather than reading it as a function being defined. Understand
# it is an object like mock instance of the DatabaseManager object being created.
# Here we apply the factory pattern, to solve our design requirements
def database_manager_factory():
    def _database_manager(sample_data):
        # This dynamically fetches the sample data based on the test, which is using the database_manager fixture
        bot_mock = MagicMock()  # create magic mock object
        symbol = 'symbol'  # Create dummy symbol string
        bot_mock.df_dict = {symbol: sample_data}  # assign dummy data to key inside dictionary
        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="VZe1x2sF1HTyLp9r27Ka",
            database="trading_bot_debug"
        )

        # Create and return a mocked DatabaseManager instance
        return database_manager_dir.DatabaseManager(bot_mock)
    return _database_manager


# Test for the deduplication_of_partial_historical_data method
def test_deduplication_of_partial_historical_data_integration(database_manager_factory, sample_date_data):
    database_manager = database_manager_factory(sample_date_data)
    conn = database_manager.conn
    # Create a table with some data for testing
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_symbol_debug (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Date DATETIME
        )
    """)
    cursor.execute("""
        INSERT INTO bot_symbol_debug (Date) VALUES 
        ('2022-01-01 00:00:00'), ('2022-01-01 00:00:00'), ('2022-01-02 00:00:00')
    """)
    conn.commit()
    try:
        # Call the method being tested
        database_manager.conn = conn
        database_manager.delete_partial = 0  # Reset delete_partial flag
        database_manager.deduplication_of_partial_historical_data('symbol', -1)

        # Verify that the duplicate row was deleted
        cursor.execute("SELECT COUNT(*) FROM bot_symbol_debug")
        count = cursor.fetchone()[0]
        assert count == 2
    finally:
        # Clean up: Drop the test table
        cursor.execute("DROP TABLE IF EXISTS bot_symbol_debug")
        conn.commit()
        conn.close()


# Test the append_data_to_mysql function
def test_append_data_to_mysql(database_manager_factory, sample_dataframe):
    # Create our mocked database object + sample data
    database_manager = database_manager_factory(sample_dataframe)

    # Connect to the database
    conn = database_manager.conn
    cursor = conn.cursor()
    # Create an empty table. The query is stored in the sample_data.py file. The table name can dynamically reflect
    # different symbols
    cursor.execute(sample_dataframe_query('symbol'))

    # Call the method being tested
    database_manager.append_data_to_mysql(database_manager.bot.df_dict['symbol'].iloc[-1], 'symbol')

    # Verify that the duplicate row was deleted
    cursor.execute("SELECT COUNT(*) FROM bot_symbol_debug")
    count = cursor.fetchone()[0]
    assert count == 1


    # Clean up: Drop the test table
    cursor.execute("DROP TABLE IF EXISTS bot_symbol_debug")
    conn.commit()
    conn.close()


# Test the append_data_to_mysql function
def test_drop_tables_if_exist(database_manager_factory, sample_dataframe):
    # Create our mocked database object + sample data
    database_manager = database_manager_factory(sample_dataframe)

    # Connect to the database
    conn = database_manager.conn
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_symbol_debug (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Date DATETIME
        )
    """)

    database_manager.bot.symbols = ["symbol"]

    # Call the method being tested
    database_manager.drop_tables_if_exist()

    # Verify that the duplicate row was deleted
    cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'bot_symbol_debug'")
    count = cursor.fetchone()[0]
    assert count == 0


    # Clean up: Drop the test table
    cursor.execute("DROP TABLE IF EXISTS bot_symbol_debug")
    conn.commit()
    conn.close()

# Test the append_data_to_mysql function
def test_update_open_candidate_row(database_manager_factory, sample_dataframe):
    # Create our mocked database object + sample data
    database_manager = database_manager_factory(sample_dataframe)

    # Connect to the database
    conn = database_manager.conn
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_symbol_debug (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Date DATETIME
        )
    """)

    database_manager.bot.symbols = ["symbol"]

    # Call the method being tested
    database_manager.drop_tables_if_exist()

    # Verify that the duplicate row was deleted
    cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'bot_symbol_debug'")
    count = cursor.fetchone()[0]
    assert count == 0


    # Clean up: Drop the test table
    cursor.execute("DROP TABLE IF EXISTS bot_symbol_debug")
    conn.commit()
    conn.close()