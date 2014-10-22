# ----------------------------------------------------------------------------
# Filename:     logger.py
# Author:       Harrison Hubbell
# Date:         10/21/2014
# Description:  Is responsible for writing to log files, can be inherited or 
#               implemented in other Smartkeg classes to provide standardized
#               logging method implementations.
# ----------------------------------------------------------------------------

from ConfigParser import ConfigParser
import logging

class SmartkegLogger(object):
    _BASE_DIR = '/usr/local/src/smartkeg/'
    
    def __init__(self, config_path):
        self.set_logger(config_path, logging.INFO)

    def set_logger(self, config_path, level):
        """
        @Author:        Harrison Hubbell
        @Created:       10/21/2014
        @Description:   Sets up the logger based on config files.
        """
        HEADER = 'SmartkegLogger'
        
        cfg = ConfigParser()
        cfg.read(config_path)
        log_dir = cfg.get(HEADER, 'dir')
        log_file = cfg.get(HEADER, 'file')
        self.log_path = self._BASE_DIR + log_dir + log_file
        
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
        if not isinstance(message, list):
            message = [message]

        logging.info(' '.join('{}'.format(i) for i in message))
