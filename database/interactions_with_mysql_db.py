from mysql.connector import Error
from sqlalchemy import create_engine, MetaData, Table
import numpy
import pandas
import os


class DatabaseInteraction:

    def __init__(self, bot):

        # Store a reference to the Bot instance
        # This allows DatabaseInteraction to communicate with the Bot, especially for passing df_dict
        self.bot = bot

        # define how to make a mysql engine
        def get_mysql_engine():
            user = 'root'
            password = os.environ.get('LOCAL_DB_PASSWORD')
            host = 'localhost'
            port = 3306
            database = 'trading_bot_debug'
            engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")
            return engine

        # make a mysql engine
        try:
            self.mysql_engine = get_mysql_engine()
            print("Connected to MySQL database using SQLAlchemy")
        except Exception as ex:
            print("Error creating MySQL engine:", ex)

        # Comment the following line to NOT drop tables
        self.drop_tables_if_exist()

    # the last bar of historical data and first bar of realtime data are the same tick, causing a duplication issue
    # this function solves that issue in the DB
    def deduplication_of_partial_historical_data(self, symbol):
        delete_partial = False  # flag for deletion of last row in historical data export (deduplication)
        table_name = f"bot_{symbol.lower()}_debug"  # find debugging tables' name
        # ensure source dataframe is not empty
        if len(self.bot.df_dict[symbol]) < 1:
            pass
        # else delete duplicate row
        else:
            last_row = self.bot.df_dict[symbol].iloc[-1]  # get the latest row (for deduplication)
            if not delete_partial:
                # Drop the row from the database where date matches the incoming (duplicate) row's date
                delete_query = f"DELETE FROM `trading_bot_debug`.`{table_name}` WHERE `Date` = '{last_row['Date']}' LIMIT 1"
                self.mysql_engine.execute(delete_query)  # execute the delete query
                #print(f"deleted duplicate row in DB for {symbol} at datetime {last_row['Date']}")
                delete_partial = True

    # append the incoming data (initially stored in dataframe) to the mysql table
    def append_data_to_mysql(self, incoming_row, symbol):
        try:
            # Generate a dynamic table name based on the symbol
            table_name = f"bot_{symbol.lower()}_debug"

            # Fix Date's datatype for conversion to MySQL
            incoming_row['Date'] = pandas.to_datetime(incoming_row['Date'])

            # Ensure last_row is a DataFrame
            if not isinstance(incoming_row, pandas.DataFrame):
                last_row = pandas.DataFrame([incoming_row], columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Date',
                                                                 'is_divergence_open_candidate',
                                                                 'paired_divergence_opens_id',
                                                                 'paired_divergence_opens_closing_price',
                                                                 'paired_divergence_opens_rsi', 'is_divergence_high',
                                                                 'rsi',
                                                                 'is_entry_candidate', 'is_entry', 'symbol'])

            # Convert float64 columns to float
            for column in incoming_row.columns:
                if incoming_row[column].dtype == 'float64':
                    incoming_row[column] = numpy.float64(incoming_row[column])

            # Append data to MySQL database using SQLAlchemy with the dynamic table name
            with self.mysql_engine.connect() as connection:
                incoming_row.to_sql(table_name, connection, if_exists='append', index=False, schema="trading_bot_debug")

        except Error as e:
            print(f"Error: {e}")
    def drop_tables_if_exist(self):
        try:
            metadata = MetaData(self.mysql_engine)
            for symbol in self.bot.symbols:
                table_name = f"bot_{symbol.lower()}_debug"
                table = Table(table_name, metadata, autoload=True)
                table.drop(self.mysql_engine)
                # print(f"Dropped table {table_name}")
        except Exception as ex:
            print(f"Error dropping tables: {ex}")



