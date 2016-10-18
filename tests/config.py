"""Testing configuration for Speranza Health backend"""
TESTING = True
WTF_CSRF_ENABLED = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///speranza_test.db'