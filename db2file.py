#!/usr/local/python
"""Tool to extract TheBox MySQL Database to an ASCII File

This script access the MySQL Database, retrieves the data and write a csv file by default. It is possible to
write the output in a different format but it will be done on request.
For backwards compatibility the old mysql-python is used instead of the latest MySQLdb

Example:
    The first time you run this script you will be prompted to enter the password for the database. Then it will
    be stored in the user's home directory in a hidden folder. It is possible to parse as arguments all the
    parameters for a given MySQL database such as: user, password, host, database and table.

        $ python2.7 db2file.py

    In the following example almost all the options are used even though all the values are the default ones

        $ python2.7 db2file.py --default-dir .thebox
                               --mysql-access-file mysqlaccess
                               --my-user thebox
                               --my-host localhost
                               --my-database theBoxData
                               --my-table temperatureAndStatusPhaseTwo
                               --output-name output
                               --output-format .csv
                               --get-all
                               --header

    The options thar are not shown in the previous example are:
        -h or --help
        --update-password

    There are also short versions available for MySQL specific arguments.
        -U --my-user
        -H --my-host
        -D --my-database
        -T --my-table

Note:
    This script complies with PEP8 and PEP257 (Google Style)

"""

import os
import sys
import argparse
import getpass
import base64
import pickle
import mysql.connector
from mysql.connector import (connection)
from mysql.connector import errorcode
from pandas import DataFrame
import logging as log
import warnings

warnings.filterwarnings('ignore')
log.basicConfig(level=log.INFO)

__author__ = 'Simon Torres'
__date__ = '2016-08-04'
__version__ = "1.0"
__email__ = "storres@ctio.noao.edu"
__status__ = "Production"


class MainApp:
    """Dumps database table into a Comma Separated Values file

    """
    table_columns = ['DATE',
                     'SENSOR_ONE',
                     'SENSOR_TWO',
                     'SENSOR_THREE',
                     'SENSOR_FOUR',
                     'SENSOR_FIVE',
                     'SENSOR_SIX',
                     'SENSOR_SEVEN',
                     'TH_SET_TEMP',
                     'TH_VAL_TEMP',
                     'TH_HEATER_ON',
                     'AIR_HEATER_ON']

    def __init__(self):
        self.args = self.get_args()
        self.access_file_name = self.args.my_file
        self.thebox_env_dir = os.path.expanduser('~/') + self.args.thebox_dir
        self.access = self.define_environment()
        self.my_connection = self.connect_mysql()
        self.cursor = self.my_connection.cursor()
        self.query_constraints = self.get_constraints()
        self.data = self.mysql_query(self.query_constraints)
        self.write_to_file()

    @staticmethod
    def get_args():
        """Handles the argparse library and returns the arguments



        Returns:
            args (class): Contains all the arguments parsed or default values

        """

        parser = argparse.ArgumentParser(description='Tool to dump TheBox MySQL Database to ASCII File.')

        parser.add_argument('--mysql-access-file',
                            action='store',
                            default='mysqlaccess',
                            type=str,
                            dest='my_file',
                            help='Name of the file that stores access information.')

        parser.add_argument('--update-password',
                            action='store_true',
                            default=False,
                            dest='set_new_password',
                            help='Request a new Password.')

        parser.add_argument('--default-dir',
                            action='store',
                            default='.thebox/',
                            type=str,
                            dest='thebox_dir',
                            help='Location of TheBox Files.')

        parser.add_argument('-U', '--my-user',
                            action='store',
                            default='thebox',
                            dest='my_user',
                            help='MySQL User Name.')

        parser.add_argument('-H', '--my-host',
                            action='store',
                            default='localhost',
                            dest='my_host',
                            help='MySQL Host Name.')

        parser.add_argument('-D', '--my-database',
                            action='store',
                            default='theBoxData',
                            dest='my_database',
                            help='MySQL Database Name.')

        parser.add_argument('-T', '--my-table',
                            action='store',
                            default='temperatureAndStatusPhaseTwo',
                            dest='table',
                            help='MySQL Table Name')

        parser.add_argument('--output-name',
                            action='store',
                            default='output',
                            dest='output_name',
                            help='Output File Name')

        parser.add_argument('--output-format',
                            action='store',
                            default='.csv',
                            dest='output_format',
                            choices=['.csv'],
                            help='Output File Name')

        parser.add_argument('--get-all',
                            action='store_false',
                            default=True,
                            dest='get_all',
                            help='Get all available data.')

        parser.add_argument('--header',
                            action='store_true',
                            default=False,
                            dest='header',
                            help='Include a header with column names in the output file.')

        """
        parser.add_argument('--skip-linearity',
                            action='store_false',
                            default=True,
                            dest='linearity',
                            help='Skip linearity correction. Helpful when you want to repeat later processes')
        """

        args = parser.parse_args()

        if args.thebox_dir[-1] != '/':
            args.thebox_dir += '/'
        # print args
        return args

    def define_environment(self):
        """Performs System checks and performs necessary actions



        Returns:
            access_data (dict): Dictionary that contains access information to be used to access MySQL database. The
            difference with the function access_info_request is that this one could be read from a file instead that
            from user input.

        """
        if os.path.isdir(self.thebox_env_dir):
            log.debug("Directory exist %s", self.thebox_env_dir)
            if os.path.isfile(self.thebox_env_dir + self.access_file_name):
                log.debug("Access file exists %s", self.thebox_env_dir + self.access_file_name)
                i_file = open(self.thebox_env_dir + self.access_file_name, 'rb')
                access_data = pickle.load(i_file)
                # print(access_data)
                if access_data['user'] != self.args.my_user:
                    access_data = self.access_info_request()
            else:
                log.debug("access File doesnt exist")
                access_data = self.access_info_request()
        else:
            log.debug("Creating directory %s", self.thebox_env_dir)
            try:
                os.path.os.mkdir(self.thebox_env_dir)
                log.debug("Directory created sucessfully")
                access_data = self.access_info_request()
            except OSError as error:
                log.debug(error)
                sys.exit(0)
        return access_data

    def access_info_request(self):
        """Request the password, formats access information and stores it in a file

        Returns:
            access_data (dict): Dictionary that contains access information to be used to access MySQL database from
            user input

        """
        log.warning("There is no environment defined please answer the questions.")
        my_password = base64.b64encode(getpass.getpass(prompt="Password (%s): " % self.args.my_user))
        access_data = {'user': self.args.my_user,
                       'password': my_password,
                       'host': self.args.my_host,
                       'database': self.args.my_database}
        my_file_name = self.thebox_env_dir + self.access_file_name
        o_file = open(my_file_name, 'wb')
        pickle.dump(access_data, o_file, protocol=pickle.HIGHEST_PROTOCOL)
        o_file.close()
        return access_data

    def connect_mysql(self):
        # print self.access
        try:
            my_connection = connection.MySQLConnection(user=self.access['user'],
                                                       password=base64.b64decode(self.access['password']),
                                                       host=self.access['host'],
                                                       database=self.access['database'])
            return my_connection
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                log.info("MySQL: Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                log.info("MySQL: Database does not exist")
            else:
                log.debug(err)

    def get_constraints(self):
        query_root = 'SELECT * FROM '
        if self.args.get_all:
            log.info('Getting all the data from table %s', self.args.table)
            my_query = ("""%s %s""" % (query_root, self.args.table))
            log.debug("MySQL Query: %s", my_query)
            return my_query
        else:
            log.info('Getting part of the data')
            log.info("I'm sorry. This part in not implemented yet.")
            return 0

    def mysql_query(self, query):
        if query != 0:
            try:
                self.cursor.execute(query)
                if self.args.header:
                    data_frame = DataFrame(self.cursor.fetchall(), columns=self.table_columns)
                else:
                    data_frame = DataFrame(self.cursor.fetchall())
                self.my_connection.commit()
                # data_frame.to_csv('everything.csv')
                return data_frame
            except mysql.connector.errors.InterfaceError:
                log.debug("MySQL: raised InterfaceError")
            except mysql.connector.errors.OperationalError:
                log.debug("MySQL: raised OperationalError")

    def write_to_file(self):
        if self.args.output_format == ".csv":
            print self.data.keys()
            self.data.to_csv(self.args.output_name + self.args.output_format, )


if __name__ == '__main__':
    App = MainApp()
