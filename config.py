"""Configuration for Speranza Health backend"""

# Statement for enabling the development environment
DEBUG = False

SQLALCHEMY_TRACK_MODIFICATIONS = "False"

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

# Specifies conncetion to azure sql server
SQLALCHEMY_DATABASE_URI = \
"mssql+pymssql://speranza-dev@speranza-server:3Treelandscaping@speranza-server.database.windows.net/speranza-db"
		#"sqlite:///speranza_test.db"


# SQLALCHEMY_POOL_SIZE = 20
# SQLALCHEMY_POOL_RECYCLE = 280
