from db_connector import Database
import logging
from datetime import datetime

logging.basicConfig(level=logging.ERROR,
                    format='%(process)d-%(levelname)s-%(message)s')


class Orders():
    def __init__(self) -> None:
        self.db_object = Database()
    # def initialise_databases():

    def check_last_update_date(self):
        try:
            results = self.db_object.query(
                'SELECT * FROM orders ORDER BY ROWID DESC LIMIT 1')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS orders (
                                        update_date TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query('SELECT * FROM orders LIMIT 1')
                # print(self.db_object.query('SELECT * FROM orders LIMIT 1'), 'DB utility 1')
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
        print(''' INSERT INTO orders(update_date)
                VALUES({0}) '''.format(datetime.today().strftime('%d-%m-%Y')), 'insert_date_entry')
        try:
            cursor = self.db_object.create_schema_with_record(
                ''' INSERT INTO orders
                VALUES(?) ''', [datetime.today().strftime('%d-%m-%Y')])
            return cursor
        except Exception as e:
            print('failure insert_date_entry', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS orders (
                                        update_date TEXT NOT NULL
                                    ); """
                )
                cursor = self.db_object.create_schema_with_record(
                    ''' INSERT INTO orders
                VALUES(?) ''', [datetime.today().strftime('%d-%m-%Y')])
                return cursor

    def insert_order(self, records):

        try:
            # self.db_object.create_schema(''' DELETE FROM orders ''')
            cursor = self.db_object.execute_one(
                '''INSERT OR IGNORE INTO orders VALUES(?,?,?)''', records
            )
            return cursor
        except Exception as e:
            print('Error insert_order', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS orders (
                                        order_id TEXT PRIMARY KEY,
                                        order_json TEXT NOT NULL,
                                        order_collection TEXT NOT NULL
                                    ); """
                )
                cursor = self.db_object.execute_one(
                    '''INSERT OR IGNORE INTO orders VALUES(?,?,?)''', records
                )
                return cursor

    def get_orders(self):
        try:
            results = self.db_object.query(
                ''' SELECT * FROM orders ORDER BY ROWID DESC''')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            print('Error get_orders', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS orders (
                                        order_id TEXT PRIMARY KEY,
                                        order_json TEXT NOT NULL,
                                        order_collection TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query(''' SELECT * FROM orders''')
                # print(self.db_object.query('SELECT * FROM orders LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []
    def get_order_by_timestamp(self,timestamp):
        print(''' SELECT * FROM orders where order_id = '{0}' '''.format(timestamp))
        try:
            results = self.db_object.query(
                ''' SELECT * FROM orders WHERE order_id = '{0}' '''.format(timestamp))
            # print(results, 'DB utility')
            return results
        except Exception as e:
            print('Error get_orders', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS orders (
                                        order_id TEXT PRIMARY KEY,
                                        order_json TEXT NOT NULL,
                                        order_collection TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query(''' SELECT * FROM orders''')
                # print(self.db_object.query('SELECT * FROM orders LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []
    def update_order_status(self,order_object,row_id):
        try:
            # self.db_object.create_schema(''' DELETE FROM orders ''')
            cursor = self.db_object.create_schema(
                ''' UPDATE orders SET order_collection = '{0}' where order_id = '{1}' '''.format(order_object,row_id)
            )
            return cursor
        except Exception as e:
            print('Error insert_order', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS orders (
                                        order_id TEXT PRIMARY KEY,
                                        order_json TEXT NOT NULL,
                                        order_collection TEXT NOT NULL
                                    ); """
                )
                cursor = self.db_object.execute_one(
                    '''INSERT OR IGNORE INTO orders VALUES(?,?,?)''', records
                )
                return cursor