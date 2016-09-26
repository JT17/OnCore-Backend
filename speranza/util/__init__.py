# global definitions
ERR_LOG = './application/logs/speranza_error.log'
DEBUG_LOG = './application/logs/speranza_debug.log'

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False