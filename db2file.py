#!/usr/local/python
"""CCD Reduction Routine for e2v camera at Swope Telescope

This pipeline performs all the necessary reduction processes for single nights

"""

import os
import sys
import time
import datetime
import argparse
import getpass
import base64
import cPickle as pickle
# import mysql.connector
# from mysql.connector import (connection)
# from mysql.connector import errorcode
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import socket
import pandas as pd
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
        self.access_file_name = 'mysqlaccess'
        self.thebox_env_dir = os.path.expanduser('~/') + '.thebox/'
        self.access = self.define_environment()
        self.my_connection = connection.MySQLConnection()

    def define_environment(self):
        """Performs System checks and performs necessary actions



        Returns:
            access_data (dict): Dictionary that contains access information to be used to access MySQL database. The
            difference with the function access_info_request is that this one could be read from a file instead that
            from user input.

        """
        if os.path.isdir(self.thebox_env_dir):
            log.debug("Directory exist %s",self.thebox_env_dir)
            if os.path.isfile(self.thebox_env_dir + self.access_file_name):
                log.debug("Access file exists")
                i_file = open(self.thebox_env_dir + self.access_file_name, 'rb')
                access_data = pickle.load(i_file)
                print(access_data)
            else:
                log.debug("access File doesnt exist")
                access_data = self.access_info_request()
        else:
            log.debug("Creating directory %s",self.thebox_env_dir)
            try:
                os.path.os.mkdir(self.thebox_env_dir)
                log.debug("Directory created sucessfully")
                access_data = self.access_info_request()
            except OSError as error:
                log.debug(error)

        return access_data

    def access_info_request(self):
        """Request the password, formats access information and stores it in a file

        Returns:
            access_data (dict): Dictionary that contains access information to be used to access MySQL database from
            user input

        """
        log.warning("There is no environment defined please answer the questions.")
        my_user = 'thebox'
        my_password = base64.b64encode(getpass.getpass(prompt="Password (%s): "%my_user))
        my_host = 'localhost'
        my_database = 'theBoxData'
        access_data = {'user' : my_user,
                       'password' : my_password,
                       'host': my_host,
                       'database' : my_database}
        my_file_name = self.thebox_env_dir + self.access_file_name
        o_file = open(my_file_name, 'wb')
        pickle.dump(access_data, o_file, protocol=pickle.HIGHEST_PROTOCOL)
        o_file.close()
        return access_data

if __name__ == '__main__':
    App = MainApp()
    # os.rmdir('/user/simon/.thebox/')