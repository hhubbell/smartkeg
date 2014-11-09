# ----------------------------------------------------------------------------
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Manages connection with MariaDB database. The current scope
#               of the project does not allow users to delete records via this
#               interface. In fact, the database user should not only have
#               INSERT and SELECT permissions.
# ----------------------------------------------------------------------------

import MySQLdb
import MySQLdb.cursors

class DatabaseInterface(object):
    def __init__(self, addr, dbn, user, pwd, logger=None):
        self.logger = logger        
        self.connect(addr, dbn, user, pwd)

    def __exit__(self):
        self.conn.close()

    def connect(self, addr, dbn, user, pwd):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Attempts to connect to the MySQL database.  Handles
                        errors if attempt fails.
        """
        try:
            self.conn = MySQLdb.connect(addr, user, pwd, dbn, cursorclass=MySQLdb.cursors.DictCursor)
            self.log_message(('[Database Interface]', 'Successfully connected to', dbn, 'as user', user))
        except MySQLdb.OperationalError as e:
            self.log_message(('[Database Interface]', 'Could not connect to the database for the following reason:', e))

    def log_message(self, message):
        """
        @Author:        Harrison Hubbell
        @Created:       10/31/2014
        @Description:   Logs a message if the logger has been specified.
        """
        if self.logger: self.logger.log(message)

    def prepare(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Gets the database cursor to prep for a transaction
        """
        self.cur = self.conn.cursor()

    def INSERT(self, query, params=None):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Makes an INSERT transaction on the database
        """
        self.prepare()
        try:
            self.cur.executemany(query, params)
            self.conn.commit()
            self.log_message(('[Database Interface]', 'Successful INSERT transaction with the following data:', '\nQuery:\n', query, '\nParams:\n', params))
        except Exception as e:
            self.conn.rollback()
            self.log_message(('[Database Interface]', 'Failed INSERT transaction:', e, '\nQuery:\n', query, '\nParams:\n', params))

    def SELECT(self, query, params=None):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Makes a SELECT transaction on the database, returns result
        """
        self.prepare()
        try:
            self.cur.execute(query, params)
            res = self.cur.fetchall()
            self.log_message(('[Database Interface]', 'Successful SELECT transaction with the following data:', '\nQuery:\n', query, '\nParams:\n', params))
        except Exception as e:
            self.conn.rollback()
            self.log_message(('[Database Interface]', 'Failed SELECT transaction:', e, '\nQuery:\n', query, '\nParams:\n', params))


        return res
