import mysql.connector
from sqlalchemy import create_engine, MetaData, Table, text
import numpy
import pandas
import traceback

#Notes
"""
-----------------
1. I encountered a mysterious bug with SQLAlchemy's execute method not being defined/used properly. It was not 
related to package version. Instead of doing a deeper debugging I used the mysqlconnector + cursor to execute my 
query to DB.

-----------------
"""

class DatabaseManager:

    def __init__(self, bot):

        # using mysqlconnector due to sqlalchemy bug, see Notes
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="VZe1x2sF1HTyLp9r27Ka",
            database="trading_bot_debug"
        )

        # Store a reference to the Bot instance
        # This allows DatabaseInteraction to communicate with the Bot, especially for passing df_dict
        self.bot = bot

        # make a mysql engine
        try:
            self.mysql_engine = self.get_mysql_engine()
            print("Connected to MySQL database using SQLAlchemy")
        except Exception as ex:
            print("Error creating MySQL engine:", ex)

        # Comment the following line to NOT drop tables
        self.drop_tables_if_exist()

        self.delete_partial = False  # flag for deletion of last row in historical data export (deduplication)

    # define how to make a mysql engine
    def get_mysql_engine(self):
        user = 'root'
        password = 'VZe1x2sF1HTyLp9r27Ka'
        host = 'localhost'
        port = 3306
        database = 'trading_bot_debug'
        engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")
        # Specify the authentication plugin in the connection string
        #engine = create_engine(
            #f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}?auth_plugin=mysql_native_password")
        return engine

    # the last bar of historical data and first bar of realtime data are the same tick, causing a duplication issue
    # this function solves that issue in the DB
    def deduplication_of_partial_historical_data(self, symbol):

        table_name = f"bot_{symbol.lower()}_debug"  # find debugging tables' name

        # ensure source dataframe is not empty
        if len(self.bot.df_dict[symbol]) < 1:
            pass

        # else delete duplicate row
        else:
            last_row = self.bot.df_dict[symbol].iloc[-1]  # get the latest row (for deduplication)

            if not self.delete_partial:
                # Drop the row from the database where date matches the incoming (duplicate) row's date

                delete_query = f"DELETE FROM `trading_bot_debug`.`{table_name}` WHERE `Date` = '{last_row['Date'].strftime('%Y-%m-%d %H:%M:%S')}'"

                try:
                    cursor = self.conn.cursor()
                    cursor.execute(delete_query, params=None, multi=False)
                    self.conn.commit()
                    cursor.close()
                    self.delete_partial = True
                except Exception as ex:
                    print(f"Error executing delete query: {ex}")
                    traceback.print_exc()

    # append the incoming data (initially stored in dataframe) to the mysql table
    def append_data_to_mysql(self, incoming_row, symbol):
        try:
            # Generate a dynamic table name based on the symbol
            table_name = f"bot_{symbol.lower()}_debug"

            # Fix Date's datatype for conversion to MySQL
            incoming_row['Date'] = pandas.to_datetime(incoming_row['Date'])

            # Force last_row to be a DataFrame
            # Force the Dataframe to have the specified columns, otherwise the index is included,
            # which sql table does not expect
            if not isinstance(incoming_row, pandas.DataFrame):
                last_row = pandas.DataFrame([incoming_row], columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Date',
                                                                 'is_divergence_open_candidate',
                                                                 'paired_divergence_opens_id',
                                                                 'paired_divergence_opens_closing_price',
                                                                 'paired_divergence_opens_rsi', 'is_divergence_high',
                                                                 'rsi',
                                                                 'is_entry_candidate', 'is_entry', 'symbol'])
            elif isinstance(incoming_row, pandas.Series):
                last_row = incoming_row.to_frame().T  # Convert Series to DataFrame with a single row
                last_row.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Date',
                                    'is_divergence_open_candidate',
                                    'paired_divergence_opens_id',
                                    'paired_divergence_opens_closing_price',
                                    'paired_divergence_opens_rsi', 'is_divergence_high',
                                    'rsi',
                                    'is_entry_candidate', 'is_entry', 'symbol']


            # Convert dataframe datatypes to mysql accepted types
            for column, value in incoming_row.items():
                if isinstance(value, numpy.float64):
                    incoming_row[column] = float(value)
                elif isinstance(value, numpy.int64):
                    incoming_row[column] = int(value)
                elif isinstance(value, pandas.Timestamp):
                    incoming_row[column] = value.strftime('%Y-%m-%d %H:%M:%S')

            # Append data to MySQL database using SQLAlchemy with the dynamic table name
            try:
                with self.mysql_engine.connect() as connection:
                    last_row.to_sql(table_name, connection, if_exists='append', index=False, schema="trading_bot_debug")
            except Exception as e:
                print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
    def drop_tables_if_exist(self):
        try:
            metadata = MetaData()
            metadata.reflect(bind=self.mysql_engine)
            for symbol in self.bot.symbols:
                table_name = f"bot_{symbol.lower()}_debug"
                if table_name in metadata.tables:
                    table = Table(table_name, metadata, autoload=True)
                    table.drop(self.mysql_engine)
                    print(f"Dropped table {table_name}")
                else:
                    print(f"Table {table_name} not found")
        except Exception as ex:
            print(f"Error dropping tables: {ex}")