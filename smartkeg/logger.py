# ----------------------------------------------------------------------------
# Filename:     logger.py
# Author:       Harrison Hubbell
# Date:         10/21/2014
# Description:  Is responsible for writing to log files, can be inherited or 
#               implemented in other Smartkeg classes to provide standardized
#               logging method implementations.
# ----------------------------------------------------------------------------

import logging
import time

class Logger(object):
    def __init__(self, directory, filename):
        self.set_logger(directory, filename, logging.INFO)

    def set_logger(self, directory, filename, level):
        """
        @Author:        Harrison Hubbell
        @Created:       10/21/2014
        @Description:   Sets up the logger based on config files.
        """
        date = time.strftime("%Y%m%d")
        self.log_path = directory + filename + date + '.log'

        logging.basicConfig(
            filename=self.log_path,
            format='%(asctime)s %(levelname)s: %(message)s',
            level=level
        )

    def log(self, message):
        """
        @Author:        Harrison Hubbell
        @Created:       10/21/2014
        @Description:   Logs a message.
        """
        if not isinstance(message, tuple):
            message = (message,)

        logging.info(' '.join('{}'.format(i) for i in message))
