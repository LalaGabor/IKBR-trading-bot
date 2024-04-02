import pytest
from unittest.mock import MagicMock
import database_manager_dir
import mysql.connector
import pandas


@pytest.fixture  # Use decorator function to turn following function definition into an argument
def database_manager():
    bot_mock = MagicMock()  # create magic mock object
    symbol = 'symbol'  # Create dummy symbol string
    test_data = {'Date': pandas.to_datetime(['2022-01-01 00:00:00', '2022-01-02 00:00:00'])}  # Create dummy data in ...
    # ...dataframe
    bot_mock.df_dict = {symbol: pandas.DataFrame(test_data)}  # assign dummy data to key inside dictionary

    # Create and return a mocked DatabaseManager instance
    return database_manager_dir.DatabaseManager(bot_mock)  # You are passing a MagicMock() object to the constructor
    # Although the constructor does not normally accept arguments, it is forced to accept mock objects


# Integration test for the deduplication_of_partial_historical_data method
def test_deduplication_of_partial_historical_data_integration(database_manager):
    # Connect to the database_manager_dir
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="VZe1x2sF1HTyLp9r27Ka",
        database="trading_bot_debug"
    )

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

    # Call the method being tested
    database_manager.conn = conn
    database_manager.delete_partial = 0  # Reset delete_partial flag
    database_manager.deduplication_of_partial_historical_data('symbol', -1)

    # Verify that the duplicate row was deleted
    cursor.execute("SELECT COUNT(*) FROM bot_symbol_debug")
    count = cursor.fetchone()[0]
    assert count == 2

    # Clean up: Drop the test table
    cursor.execute("DROP TABLE IF EXISTS bot_symbol_debug")
    conn.commit()
    conn.close()
