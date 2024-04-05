import pytest
from unittest.mock import MagicMock
import database_manager_dir
import sqlalchemy


# MagicMock constructor function
@pytest.fixture
def bot_mock():
    return MagicMock()


# Create mock DatabaseManager object
@pytest.fixture
def database_manager(bot_mock):
    return database_manager_dir.DatabaseManager(bot_mock)


# Test case for the get_mysql_engine method
def test_get_mysql_engine(bot_mock):
    # Create a DatabaseManager instance with the mock Bot
    database_manager = database_manager_dir.DatabaseManager(bot_mock)

    # Call the method being tested
    mysql_engine = database_manager.get_mysql_engine()

    # Assert that the method returned an instance of SQLAlchemy's Engine
    assert isinstance(mysql_engine, sqlalchemy.engine.Engine)
