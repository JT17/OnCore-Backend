"""Testing configuration for Speranza Health backend"""
TESTING = True
WTF_CSRF_ENABLED = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mssql+pymssql://speranza-dev@speranza-server:3Treelandscaping@speranza-server.database.windows.net/speranza-db"