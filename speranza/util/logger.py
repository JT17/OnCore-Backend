import logging
from logging import  ERROR
from logging.handlers import TimedRotatingFileHandler
from speranza.util import ERR_LOG

class ContextualFilter(logging.Filter):

    def filter(self, log_record):
        log_record.url = request.path
        log_record.method = request.method
        log_record.ip = request.environ.get("REMOTE_ADDR")

        return True

def add_contextual_filter(application):
    context_provider = ContextualFilter()
    application.logger.addFilter(context_provider)
    handler = logging.StreamHandler()

    log_format = "%(asctime)s\t%(levelname)s\t%(user_id)s\t%(ip)s\t%(method)s\t%(url)s\t%(message)s"
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    # Finally, attach the handler to our logger
    application.logger.addHandler(handler)
    return application

def set_up_error_handling(application):
    file_handler = TimedRotatingFileHandler(ERR_LOG, when="D", backupCount=7)

    # Use a multi-line format for this logger, for easier scanning
    file_formatter = logging.Formatter('''
        Time: %(asctime)s
        Level: %(levelname)s
        Method: %(method)s
        Path: %(url)s
        IP: %(ip)s
        User ID: %(user_id)s

        Message: %(message)s

        ---------------------''')

    # Filter out all log messages that are lower than Error.
    file_handler.setLevel(ERROR)

    file_handler.setFormatter(file_formatter)
    application.logger.addHandler(file_handler)
    return application

def set_up_logging(application):
    application = add_contextual_filter(application)
    application = set_up_error_handling(application)
    return application
