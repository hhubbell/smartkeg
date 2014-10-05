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
    def __init__(self, addr, dbn, user, pwd):
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
        except MySQLdb.OperationalError as e:
            print "Could not connect to the database:"
            print e
            
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
        except:
            self.conn.rollback()

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
        except:
            self.conn.rollback()
        
        return res
