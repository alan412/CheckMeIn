import sqlite3
import os
from enum import IntEnum

class Status(IntEnum):
    inactive = 0
    active = 1

class Keyholders(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version < 4:
            dbConnection.execute('''CREATE TABLE keyholders
                                 (barcode TEXT PRIMARY KEY, active INTEGER default 0)''')

    def removeKeyholder(self, dbConnection):
        dbConnection.execute("UPDATE keyholders SET active = ? WHERE (active==?)",
                             (Status.inactive, Status.active))

    def setActiveKeyholder(self, dbConnection, barcode):
        if barcode:
            self.removeKeyholder(dbConnection)
            dbConnection.execute(
                "UPDATE keyholders SET active = ? WHERE (barcode==?)", (Status.active, barcode))


    def getActiveKeyholder(self, dbConnection):
        """Returns the (barcode, name) of the active keyholder"""
        data = dbConnection.execute(
            '''SELECT keyholders.barcode, displayName FROM keyholders 
               INNER JOIN members ON keyholders.barcode = members.barcode
               WHERE active==?''', (Status.active,)).fetchone()
        if data is None:
            return ('', '')
        else:
            return (data[0], data[1])