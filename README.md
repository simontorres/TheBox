# TheBox

This Repository contains tools developed and used for the operation of 
TheBox Experiment at the University of Goettingen, Germany.

## What it Contains:

### db2file.py
This scripts reads the MySQL database in which TheBox logs all the
temperature data. This information is written to a text file
by default it writes to **_output.csv_** (i.e. to a comma separated value format)
It is possible to generate outputs in other formats but it will be done
on request.

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
    This script complies with [PEP8](https://www.python.org/dev/peps/pep-0008/) and [PEP257](https://www.python.org/dev/peps/pep-0257/) ([Google Style Docstrings](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html))
 
Software Specific for TheBox Experiment
