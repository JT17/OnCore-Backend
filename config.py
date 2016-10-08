"""Configuration for Speranza Health backend"""

import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'speranza.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "3treelandscaping"

# Secret key for signing cookies
SECRET_KEY = "dsaf0897sfdg45sfdgfdsaqzdf98sdf0a"

# Enable protection agains *Cross-site Request Forgery (CSRF)*
WTF_CSRF_ENABLED = True

# edit the URI below to add your RDS password and your AWS URL
# The other elements are the same as used in the tutorial
# format: (user):(password)@(db_identifier).amazonaws.com:3306/(db_name)

# SQLALCHEMY_DATABASE_URI =
# 'mysql+pymysql://speranzaadmin:tunesquad3@speranzabeta.c0hrd44urhuf.sa-east-1.rds.amazonaws.com:3306/betajunedb'

# SQLALCHEMY_POOL_SIZE = 20
# SQLALCHEMY_POOL_RECYCLE = 280
