# ----------------------------------------------------------------------------
# Filename:     main.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Manages connection with MariaDB database. The current scope
#               of the project does not allow users to delete records via this
#               interface. In fact, the database user should not only have 
#               INSERT and SELECT permissions.
# TODO:         Gracefully handle errors, particularly:
#                   > Failed database connection attempts
#                   > Failed INSERT transactions
#                   > Failed SELECT transactions
# ----------------------------------------------------------------------------

import MySQLdb

class Database_Interface(object):    
    def __init__(self, addr, dbn, user, pwd):
        self.conn = MySQLdb.connect(addr, user, pwd, dbn)

    def __exit__(self):
        self.conn.close()

    def prepare(self):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Gets the database cursor to prep for a transaction
        """
        self.cur = self.conn.cursor()

    def INSERT(self, query, params):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Makes an INSERT transaction on the database
        """
        self.prepare()
        self.cur.executemany(query, params)
        self.database.commit()

    def SELECT(self, query, params):
        """
        @Author:        Harrison Hubbell
        @Created:       09/01/2014
        @Description:   Makes a SELECT transaction on the database, returns result
        """
        self.prepare()
        self.cur.execute(query, params)
        return self.cur.fetchall()
