import platform
import logging
import os
logging.basicConfig(
    filename= os.path.dirname(os.path.realpath(__file__)) + '\copy_trader.log',
    # filename = 'copy_trader.log',
    filemode='a',
    level=logging.INFO,
    format="[%(asctime)s:%(filename)s:%(lineno)s - %(funcName)20s()] %(message)s")
import sqlite3
from sqlite3 import Error
try:
    class Database():
        
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                print('Creating the object')
                cls._instance = super(Database, cls).__new__(cls)
            return cls._instance
        def __init__(self,database_name = '/home/jayant/Desktop/copy_trader.db') -> None:
            # raise TypeError('Tests')
            if platform.system() != 'Linux':
                database_name = './copy_trader.db'
            self.database_name = database_name
            try:
                self.connection = sqlite3.connect(self.database_name)
            except Error as e:
                raise e
            pass
        def create_schema(self,query):
            try:
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                return cursor.lastrowid
            except Error as e:
                raise e
        def create_schema_with_record(self,query,record):
            try:
                cursor = self.connection.cursor()
                cursor.execute(query,record)
                self.connection.commit()
                return cursor.lastrowid
            except Error as e:
                raise e
        def execute_many(self,query,records):
            try:
                cursor = self.connection.cursor()
                cursor.executemany(query,records)
                self.connection.commit()
                return cursor.rowcount
            except Error as e:
                raise e


        def execute_one(self,query,record):
            try:
                cursor = self.connection.cursor()
                cursor.execute(query,record)
                self.connection.commit()
                return cursor.rowcount
            except Error as e:
                raise e
            
        def query(self,query):
            try:
                cursor = self.connection.cursor()
                cursor.execute(query)
                records = cursor.fetchall()
                self.connection.commit()
                return records
            except Error as e:
                raise e
except Exception as e:
    log = logging.getLogger()
    log.critical(e)