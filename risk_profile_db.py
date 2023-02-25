from db_connector import Database
import logging
from datetime import datetime

logging.basicConfig(level=logging.ERROR,
                    format='%(process)d-%(levelname)s-%(message)s')


class RiskProfile():
    def __init__(self) -> None:
        self.db_object = Database()
    # def initialise_databases():

    def get_risk_profile_names(self):
        try:
            results = self.db_object.query(
                'SELECT profile_name FROM risk_profiles ORDER BY ROWID DESC')
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS risk_profiles (
                                        profile_name TEXT NOT NULL,
                                        profile_settings TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query(
                    'SELECT * FROM risk_profiles ORDER BY ROWID DESC')
                # print(self.db_object.query('SELECT * FROM updates_date_angel LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []

    def get_risk_profile_by_name(self, profile_name):
        try:
            results = self.db_object.query(
                ''' SELECT profile_settings FROM risk_profiles WHERE profile_name = '{0}' '''
                .format(profile_name)
                )
            # print(results, 'DB utility')
            return results
        except Exception as e:
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS risk_profiles (
                                        profile_name TEXT NOT NULL,
                                        profile_settings TEXT NOT NULL
                                    ); """
                )
                results = self.db_object.query(
                    
                    ''' SELECT profile_settings FROM risk_profiles WHERE profile_name = '{0}' '''
                .format(profile_name)
                    )
                # print(self.db_object.query('SELECT * FROM updates_date_angel LIMIT 1'), 'DB utility 1')
                return results
            else:
                return []

    def insert_risk_profile_by_name(self, records):
        print(records)
        try:

            cursor = self.db_object.execute_many(
                '''INSERT OR IGNORE INTO risk_profiles VALUES(?,?)''', records
            )
            return cursor
        except Exception as e:
            print('Error risk_profiles', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS risk_profiles (
                                        profile_name TEXT NOT NULL,
                                        profile_settings TEXT NOT NULL
                                    ); """
                )
                cursor = self.db_object.execute_many(
                    '''INSERT OR IGNORE INTO risk_profiles VALUES(?,?)''', records
                )
                return cursor

    def update_risk_profile_by_name(self, name, profile):
        try:

            cursor = self.db_object.create_schema(
                ''' UPDATE risk_profiles SET profile_settings = '{0}' where profile_name = '{1}'
                '''.format(profile,name)
            )
            print(name,cursor)
            return True
        except Exception as e:
            print('Error risk_profiles', e)
            if 'no such table' in repr(e):
                self.db_object.create_schema(
                    """ CREATE TABLE IF NOT EXISTS risk_profiles (
                                        profile_name TEXT NOT NULL,
                                        profile_settings TEXT NOT NULL
                                    ); """
                )
                cursor = self.db_object.create_schema(
                    ''' UPDATE risk_profiles set profile_settings = '{0}' where profile_name = {1}
                '''.format(profile,name)
                )
                return True
