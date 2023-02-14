from db_connector import Database
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(process)d-%(levelname)s-%(message)s')


class Account_DB():
    def __init__(self) -> None:
        self.db_object = Database()
    # def initialise_databases():

    def check_last_update_date(self):
        try:
            results = self.db_object.query(
                'SELECT * FROM accounts ORDER BY ROWID DESC LIMIT 1')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS accounts (
                                        update_date TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query('SELECT * FROM updates_date_zerodha LIMIT 1')
                # print(self.db_object.query('SELECT * FROM updates_date_zerodha LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []


    def insert_account_single_entry(self, records):
# instrument_token, exchange_token, tradingsymbol, name, last_price, expiry, strike, tick_size, lot_size, instrument_type, segment, exchange
        try:
            # self.db_object.create_schema(''' DELETE FROM accounts ''')
            cursor = self.db_object.execute_one(
                '''INSERT OR IGNORE INTO accounts VALUES(?,?,?,?,?,?)''', records
            )
            return cursor
        except Exception as e:
            print('Error insert_account_single_entry', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS accounts (
                                        client_id TEXT PRIMARY KEY,
                                        password TEXT NOT NULL,
                                        api_key TEXT NOT NULL,
                                        secret_key TEXT NOT NULL,
                                        totp_key TEXT NOT NULL,
                                        broker TEXT
                                    ); """
                )
                cursor = self.db_object.execute_many(
                    '''INSERT OR IGNORE INTO accounts VALUES(?,?,?,?,?,?)''', records
                )
                return cursor

    def get_accounts_data(self):
        try:
            results = self.db_object.query(
                ''' SELECT * FROM accounts ''')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS accounts (
                                        client_id TEXT PRIMARY KEY,
                                        password TEXT NOT NULL,
                                        api_key TEXT NOT NULL,
                                        secret_key TEXT NOT NULL,
                                        totp_key TEXT NOT NULL,
                                        broker TEXT
                                    ); """
                )
                results = self.db_object.query(''' SELECT * FROM accounts''')
                # print(self.db_object.query('SELECT * FROM updates_date_zerodha LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []

    def get_specific_instruments_data(self,symbol_token):
        try:
            results = self.db_object.query(
                ''' SELECT * FROM instruments_zerodha WHERE exchange_token = '{0}' LIMIT 1'''.format(symbol_token))
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
