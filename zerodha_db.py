from db_connector import Database
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(process)d-%(levelname)s-%(message)s')


class ZerodhaInstruments():
    def __init__(self) -> None:
        self.db_object = Database()
    # def initialise_databases():

    def check_last_update_date(self):
        try:
            results = self.db_object.query(
                'SELECT * FROM updates_date_zerodha ORDER BY ROWID DESC LIMIT 1')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS updates_date_zerodha (
                                        update_date TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query('SELECT * FROM updates_date_zerodha LIMIT 1')
                # print(self.db_object.query('SELECT * FROM updates_date_zerodha LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []

    def insert_date_entry(self):
        """
        Create a new project into the projects table
        :param conn:
        :param project:
        :return: project id
        """
        # sql =
        print(''' INSERT INTO updates_date_zerodha(update_date)
                VALUES({0}) '''.format(datetime.today().strftime('%d-%m-%Y')), 'insert_date_entry')
        try:
            cursor = self.db_object.create_schema_with_record(
                ''' INSERT INTO updates_date_zerodha
                VALUES(?) ''', [datetime.today().strftime('%d-%m-%Y')])
            return cursor
        except Exception as e:
            print('failure insert_date_entry', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS updates_date_zerodha (
                                        update_date TEXT NOT NULL
                                    ); """
                )
                cursor = self.db_object.create_schema_with_record(
                    ''' INSERT INTO updates_date_zerodha
                VALUES(?) ''', [datetime.today().strftime('%d-%m-%Y')])
                return cursor

    def insert_instruments_data(self, records):
# instrument_token, exchange_token, tradingsymbol, name, last_price, expiry, strike, tick_size, lot_size, instrument_type, segment, exchange
        try:
            self.db_object.create_schema(''' DELETE FROM instruments_zerodha ''')
            cursor = self.db_object.execute_many(
                '''INSERT OR IGNORE INTO instruments_zerodha VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', records
            )
            return cursor
        except Exception as e:
            print('Error insert_instruments_data', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS instruments_zerodha (
                                        instrument_token TEXT PRIMARY KEY,
                                        exchange_token TEXT NOT NULL,
                                        tradingsymbol TEXT NOT NULL,
                                        name TEXT NOT NULL,
                                        last_price TEXT NOT NULL,
                                        expiry TEXT,
                                        strike TEXT,
                                        tick_size TEXT,
                                        lot_size TEXT,
                                        instrument_type TEXT,
                                        segment TEXT NOT NULL,
                                        exchange TEXT NOT NULL
                                    ); """
                )
                cursor = self.db_object.execute_many(
                    '''INSERT OR IGNORE INTO instruments_zerodha VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', records
                )
                return cursor

    def get_instruments_data(self):
        try:
            results = self.db_object.query(
                ''' SELECT * FROM instruments_zerodha WHERE exch_seg = 'NFO' LIMIT 5''')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS instruments_zerodha (
                                        instrument_token TEXT PRIMARY KEY,
                                        exchange_token TEXT NOT NULL,
                                        tradingsymbol TEXT NOT NULL,
                                        name TEXT NOT NULL,
                                        last_price TEXT NOT NULL,
                                        expiry TEXT,
                                        strike TEXT,
                                        tick_size TEXT,
                                        lot_size TEXT,
                                        instrument_type TEXT,
                                        segment TEXT NOT NULL,
                                        exchange TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query(''' SELECT * FROM instruments_zerodha WHERE exch_seg = 'NFO' LIMIT 5''')
                # print(self.db_object.query('SELECT * FROM updates_date_zerodha LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []
