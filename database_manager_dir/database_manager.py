import mysql.connector
from sqlalchemy import create_engine, MetaData, Table, text
import numpy
import pandas
import traceback
import os
from dotenv import load_dotenv
#Notes
"""
-----------------
1. I encountered a mysterious issue with SQLAlchemy's execute method not being defined/used properly. It was not 
related to package version. Instead of doing a deeper debugging I used the mysqlconnector + cursor to execute my 
query to DB.
-----------------
"""


class DatabaseManager:

    def __init__(self, bot):
        try:
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
                print("Connected to MySQL database_manager_dir using SQLAlchemy")
            except Exception as ex:
                print("Error creating MySQL engine:", ex)

            # Comment the following line to NOT drop tables
            self.drop_tables_if_exist()

            self.delete_partial = 0  # flag for deletion of last row in historical data export (deduplication)

        except Exception as e:
            print(f"Error initializing Database Manager object: {e}")
            traceback.print_exc()

    # Get the environment variables for instantiating connection to mysql DB
    load_dotenv()

    # Define how to make a mysql engine
    def get_mysql_engine(self):
        try:
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            host = os.getenv("HOST")
            port = os.getenv("PORT")
            database = os.getenv("DATABASE")
            engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")
            return engine

        except Exception as e:
            print(f"Error creating mysql engine: {e}")
            traceback.print_exc()
    # the last bar of historical data and first bar of realtime data are the same tick, causing a duplication issue
    # this function solves that issue in the DB

    def deduplication_of_partial_historical_data(self, symbol, row_number):
        try:
            table_name = f"bot_{symbol.lower()}_debug"  # find debugging tables' name

            # ensure source dataframe is not empty
            if len(self.bot.df_dict[symbol]) < 1:
                pass

            # else delete duplicate row
            else:

                last_row = self.bot.df_dict[symbol].iloc[row_number]  # get the latest row (for deduplication)
                if self.delete_partial < 2:
                    # Drop the row from the database_manager_dir where date matches the incoming (duplicate) row's date

                    delete_query = f"""
                                    DELETE FROM `trading_bot_debug`.`{table_name}`
                                    WHERE 1=1
                                    AND year(`Date`)  = year('{last_row['Date'].strftime('%Y-%m-%d %H:%M:%S')}')
                                    AND month(`Date`) = month('{last_row['Date'].strftime('%Y-%m-%d %H:%M:%S')}')
                                    AND day(`Date`) = day('{last_row['Date'].strftime('%Y-%m-%d %H:%M:%S')}')
                                    AND hour(`Date`) = hour('{last_row['Date'].strftime('%Y-%m-%d %H:%M:%S')}')
                                    AND minute(`Date`) = minute('{last_row['Date'].strftime('%Y-%m-%d %H:%M:%S')}')
                                    """

                    # use a cursor to pass the delete_query to the DB
                    try:
                        cursor = self.conn.cursor()
                        cursor.execute(delete_query, params=None, multi=False)
                        self.conn.commit()
                        cursor.close()
                        self.delete_partial += 1  # increment flag to only deduplicate first rows
                    except Exception as ex:
                        print(f"Error executing delete query: {ex}")
                        traceback.print_exc()

        except Exception as ex:
            print(f"Error deduplicating data: {ex}")
            traceback.print_exc()
    # append the incoming data (initially stored in dataframe) to the mysql table

    def append_data_to_mysql(self, incoming_row, symbol):
        try:
            # Generate a dynamic table name based on the symbol
            table_name = f"bot_{symbol.lower()}_debug"

            # Fix Date's datatype for conversion to MySQL
            incoming_row['Date'] = pandas.to_datetime(incoming_row['Date'])
            # Force last_row to be a DataFrame
            # Force the Dataframe to have the specified columns, otherwise the index is included,...
            # ...which sql table does not expect
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

            # Append data to MySQL database_manager_dir using SQLAlchemy with the dynamic table name
            try:
                with self.mysql_engine.connect() as connection:
                    last_row.to_sql(table_name, connection, if_exists='append', index=False, schema="trading_bot_debug")
            except Exception as e:
                print(f"Error executing append query: {e}")
                traceback.print_exc()
        except Exception as e:
            print(f"Error appending data: {e}")
            traceback.print_exc()

    # Drop tables from database_manager_dir on script start (assuming you don't want history stored), see flag in main
    def drop_tables_if_exist(self):
        try:
            metadata = MetaData()  # get a metadata object to execute a drop query in DB
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
            traceback.print_exc()
    # rows are processed as the come in and thus appended. Some functions though will update previous rows in
    # dataframe and this updates those rows in the DB

    def update_open_candidate_row(self, symbol, row_number, table_name=None):
        try:
            if table_name is None:  # Conditional to allow for passing a table name during testing
                table_name = f"bot_{symbol.lower()}_debug"  # find table related to passed symbol name

            # ensure source dataframe is long enough
            if len(self.bot.df_dict[symbol]) < 12:
                pass

            # else delete duplicate row
            else:
                update_row = self.bot.df_dict[symbol].iloc[row_number - 5]  # get the latest row (for deduplication)
                update_query = f"UPDATE `trading_bot_debug`.`{table_name}` " \
                               f"SET `is_divergence_open_candidate` = {update_row['is_divergence_open_candidate']} " \
                               f" WHERE `Date` = '{update_row['Date'].strftime('%Y-%m-%d %H:%M:%S')}'"

                # use a cursor to pass the delete_query to the DB
                try:
                    cursor = self.conn.cursor()
                    cursor.execute(update_query, params=None, multi=False)
                    self.conn.commit()
                    cursor.close()
                except Exception as ex:
                    print(f"Error executing update query: {ex}")
                    traceback.print_exc()

        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
