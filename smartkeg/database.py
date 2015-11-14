#
# Filename:     database.py
# Author:       Harrison Hubbell
# Date:         09/01/2014
# Description:  Manages connections and transactions with MySQL databases.
#

import mysql.connector
import logging

class DatabaseInterface(object):
    def __init__(self, addr, dbn, user, pwd):
        self.conn = self.connect(addr, dbn, user, pwd)
        self.cur = None

    def __del__(self):
        self.conn.close()

    def __enter__(self):
        self.prepare()
        return self

    def __exit__(self, exc, value, trace):
        self.finish()

    def connect(self, addr, dbn, user, pwd):
        """
        @author:        Harrison Hubbell
        @created:       10/05/2014
        @description:   Attempts to connect to the MySQL database.
                        Handles errors if attempt fails.
        """
        try:
            return mysql.connector.connect(
                user=user,
                password=pwd,
                host=addr,
                database=dbn
            )
        except mysql.connector.Error as e:
            logging.error(
                'The following error occured during connection: %s',
                e
            )

    def prepare(self):
        """
        @author:        Harrison Hubbell
        @created:       09/01/2014
        @description:   Gets the database cursor to prep for a transaction
        """
        self.cur = self.conn.cursor(dictionary=True)

    def finish(self):
        """
        @author:        Harrison Hubbell
        @created:       09/18/2015
        @description:   Closes the database cursor
        """
        self.cur.close()

    def insert(self, query, params=None):
        """
        @author:        Harrison Hubbell
        @created:       09/01/2014
        @description:   Makes an INSERT transaction on the database
        """
        try:
            self.cur.executemany(query, params)
            self.conn.commit()
        except mysql.connector.Error as e:
            self.conn.rollback()
            logging.error(
                'Failed INSERT transaction: %s\nQuery:\n%s\nparams:\n%s',
                e, query, params
            )

    def select(self, query, params=None):
        """
        @author:        Harrison Hubbell
        @created:       09/01/2014
        @description:   Makes a SELECT transaction on the database
                        and returns result
        """
        res = None
        try:
            self.cur.execute(query, params)
            res = self.cur.fetchall()
        except mysql.connector.Error as e:
            self.conn.rollback()
            logging.error(
                'Failed SELECT transaction: %s\nQuery:\n%s\nparams:\n%s',
                e, query, params
            )

        return res

    def update(self, query, params=None):
        """
        @author:        Harrison Hubbell
        @created:       11/24/2014
        @description:   Makes an UPDATE transaction on the database
        """
        try:
            self.cur.execute(query, params)
            self.conn.commit()
        except mysql.connector.Error as e:
            self.conn.rollback()
            logging.error(
                'Failed UPDATE transaction: %s\nQuery:\n%s\nparams:\n%s',
                e, query, params
            )
