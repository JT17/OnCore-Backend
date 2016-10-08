import logging
import logging.handlers
import sys

# http://stackoverflow.com/questions/16061641/python-logging-split-between-stdout-and-stderr
class InfoFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO)


# Logging
###############################
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

h1 = logging.StreamHandler(stream=sys.stdout)
h1.setLevel(logging.DEBUG)
h1.setFormatter(formatter)
h1.addFilter(InfoFilter())
h2 = logging.StreamHandler()
h2.setLevel(logging.WARNING)
h2.setFormatter(formatter)

logger.addHandler(h1)
logger.addHandler(h2)
###############################
