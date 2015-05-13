# ----------------------------------------------------------------------------
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Manages connection with MariaDB database. The current scope
#               of the project does not allow users to delete records via this
#               interface. In fact, the database user should only have
#               INSERT, UPDATE, and SELECT permissions.
# ----------------------------------------------------------------------------

import mysql.connector

class DatabaseInterface(object):
    def __init__(self, addr, dbn, user, pwd, logger=None):
        self.logger = logger        
        self.conn = self.connect(addr, dbn, user, pwd)

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
            return mysql.connector.connect(
                user=user,
                password=pwd,
                host=addr,
                database=dbn
            )
        except mysql.connector.Error as e:
            self.log_message(('[Database Interface]', 'The following error occured during connection:', e))

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
        return self.conn.cursor(dictionary=True)

    def INSERT(self, query, params=None):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Makes an INSERT transaction on the database
        """
        cur = self.prepare()
        try:
            cur.executemany(query, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.log_message(('[Database Interface]', 'Failed INSERT transaction:', e, '\nQuery:\n', query, '\nParams:\n', params))

        cur.close()

    def SELECT(self, query, params=None):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Makes a SELECT transaction on the database, returns result
        """
        cur = self.prepare()
        try:
            cur.execute(query, params)
            res = cur.fetchall()
        except Exception as e:
            self.conn.rollback()
            self.log_message(('[Database Interface]', 'Failed SELECT transaction:', e, '\nQuery:\n', query, '\nParams:\n', params))

        cur.close()

        return res

    def UPDATE(self, query, params=None):
        """
        @Author:        Harrison Hubbell
        @Created:       11/24/2014
        @Description:   Makes an UPDATE transaction on the database
        """
        cur = self.prepare()
        try:
            cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.log_message(('[Database Interface]', 'Failed UPDATE transaction:', e, '\nQuery:\n', query, '\nParams:\n', params))

        cur.close()
