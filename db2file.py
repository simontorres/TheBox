#!/usr/local/python
"""Tool to DUMP TheBox MySQL Database to an ASCII File

This script access the MySQL Database and retrieve the data
For backwards compatibility the old mysql-python is used instead of the latest MySQLdb

Note:
    This script complies with PEP8 and PEP257 (Google Style)


"""

import os
import sys
# import time
# import datetime
import argparse
import getpass
import base64
import cPickle
# import mysql.connector
# from mysql.connector import (connection)
# import MySQLdb.connections as connection
# from mysql.connector import errorcode
# import socket
# import pandas as pd
import logging as log
import warnings

warnings.filterwarnings('ignore')
log.basicConfig(level=log.DEBUG)

__author__ = 'Simon Torres'
__date__ = '2016-08-04'
__version__ = "0.1"
__email__ = "storres@ctio.noao.edu"
__status__ = "Development"


class MainApp:
    """Dumps database table into a Comma Separated Values file

    """

    def __init__(self):
        self.args = self.get_args()
        self.access_file_name = self.args.my_file
        self.thebox_env_dir = os.path.expanduser('~/') + self.args.thebox_dir
        self.access = self.define_environment()
        # self.my_connection = connection.MySQLConnection()

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

        parser.add_argument('T', '--table-name',
                            action='store',
                            default='temperatureAndStatusPhaseTwo',
                            dest='table',
                            help='MySQL Table Name')
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
        print args
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
                access_data = cPickle.load(i_file)
                # print(access_data)
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
        cPickle.dump(access_data, o_file, protocol=cPickle.HIGHEST_PROTOCOL)
        o_file.close()
        return access_data


if __name__ == '__main__':
    App = MainApp()
