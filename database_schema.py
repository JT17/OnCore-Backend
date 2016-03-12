from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode

DB_NAME = ''

TABLES = {}
TABLES['patients'] = (
    "CREATE TABLE `patients` ("
    "  `nfc_tag` int(11) NOT NULL,"
    "  `phone_number` date NOT NULL,"
    "  `birth_date` date,"
    "  `first_name` varchar(14),"
    "  `last_name` varchar(16),"
    "  `gender` enum('M','F'),"
    "  PRIMARY KEY (`nfc_tag`)"
    ") ENGINE=InnoDB")

TABLES['patient_history'] = (
    "CREATE TABLE `patient_history` ("
    "  `nfc_tag` int(11) NOT NULL,"
    "  `event_type` varchar(40) NOT NULL,"
    "  `date` date NOT NULL, "
    "  `location` varchar(40),"
    "  PRIMARY KEY (`nfc_tag`)"
    ") ENGINE=InnoDB")

TABLES['upcoming_appointments'] = (
    "CREATE TABLE `upcoming_appointments` ("
    "  `nfc_tag` int(11) NOT NULL,"
    "  `date` date NOT NULL,"
    "  `location` varchar(40),"
    "  PRIMARY KEY (`nfc_tag`)"
    ") ENGINE=InnoDB")

config = {
	'host': 'testoncoreinstance.cmzfo5lzx48b.us-east-1.rds.amazonaws.com',
	'user': 'oncoreadmin',
	'password': 'tunesquad3',
	'db': 'testdb'
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def delete_database(cursor):
    try:
        cursor.execute("DROP DATABASE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = DB_NAME    
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        # create_database(cursor)
        delete_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

# for name, ddl in TABLES.iteritems():
#     try:
#         print("Creating table {}: ".format(name), end='')
#         cursor.execute(ddl)
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
#             print("already exists.")
#         else:
#             print(err.msg)
#     else:
#         print("OK")

cursor.close()
cnx.close()