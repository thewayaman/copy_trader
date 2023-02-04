from db_connector import Database
import logging
from datetime import datetime

logging.basicConfig(level=logging.ERROR,
                    format='%(process)d-%(levelname)s-%(message)s')


class AngelInstruments():
    def __init__(self) -> None:
        self.db_object = Database()
    # def initialise_databases():

    def check_last_update_date(self):
        try:
            results = self.db_object.query(
                'SELECT * FROM updates_date_angel ORDER BY ROWID DESC LIMIT 1')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS updates_date_angel (
                                        update_date TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query('SELECT * FROM updates_date_angel LIMIT 1')
                # print(self.db_object.query('SELECT * FROM updates_date_angel LIMIT 1'), 'DB utility 1')
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
        print(''' INSERT INTO updates_date_angel(update_date)
                VALUES({0}) '''.format(datetime.today().strftime('%d-%m-%Y')), 'insert_date_entry')
        try:
            cursor = self.db_object.create_schema_with_record(
                ''' INSERT INTO updates_date_angel
                VALUES(?) ''', [datetime.today().strftime('%d-%m-%Y')])
            return cursor
        except Exception as e:
            print('failure insert_date_entry', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS updates_date_angel (
                                        update_date TEXT NOT NULL
                                    ); """
                )
                cursor = self.db_object.create_schema_with_record(
                    ''' INSERT INTO updates_date_angel
                VALUES(?) ''', [datetime.today().strftime('%d-%m-%Y')])
                return cursor

    def insert_instruments_data(self, records):

        try:
            self.db_object.create_schema(''' DELETE FROM instruments_angel ''')
            cursor = self.db_object.execute_many(
                '''INSERT OR IGNORE INTO instruments_angel VALUES(?,?,?,?,?,?,?,?,?)''', records
            )
            return cursor
        except Exception as e:
            print('Error insert_instruments_data', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS instruments_angel (
                                        token TEXT PRIMARY KEY,
                                        symbol TEXT NOT NULL,
                                        name TEXT NOT NULL,
                                        expiry TEXT,
                                        strike TEXT,
                                        lotsize TEXT,
                                        instrumenttype TEXT,
                                        exch_seg TEXT NOT NULL,
                                        tick_size TEXT
                                    ); """
                )
                cursor = self.db_object.execute_many(
                    '''INSERT OR IGNORE INTO instruments_angel VALUES(?,?,?,?,?,?,?,?,?)''', records
                )
                return cursor

    def get_instruments_data(self):
        try:
            results = self.db_object.query(
                ''' SELECT * FROM instruments_angel WHERE exch_seg = 'NFO' ''')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS instruments_angel (
                                        token TEXT PRIMARY KEY,
                                        symbol TEXT NOT NULL,
                                        name TEXT NOT NULL,
                                        expiry TEXT,
                                        strike TEXT,
                                        lotsize TEXT,
                                        instrumenttype TEXT,
                                        exch_seg TEXT NOT NULL,
                                        tick_size TEXT
                                    ); """
                )
                results = self.db_object.query(''' SELECT * FROM instruments_angel WHERE exch_seg = 'NFO' LIMIT 5''')
                # print(self.db_object.query('SELECT * FROM updates_date_angel LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []
