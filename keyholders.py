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
        data = dbConnection.execute(
            "SELECT barcode FROM keyholders WHERE active==?", (Status.active,)).fetchone()
        if data is None:
            return ''
        else:
            return data[0]


# unit test
if __name__ == "__main__":  # pragma no cover
    DB_STRING = 'data/test.db'
    try:
        os.remove(DB_STRING)   # Start with a new one
    except:
        pass  # Don't care if it didn't exist
    keyholders = Keyholders()

    with sqlite3.connect(DB_STRING) as c:
        keyholders.migrate(c, 0)
        keyholders.setActiveKeyholder(c, '100090')
        print("Active: ", keyholders.getActiveKeyholder(c))

        keyholders.setActiveKeyholder(c, '100091')
        print("Active: ", keyholders.getActiveKeyholder(c))

        keyholders.setActiveKeyholder(c, '100090')
        print("Active: ", keyholders.getActiveKeyholder(c))

        keyholders.setActiveKeyholder(c, '')
        print("Active: ", keyholders.getActiveKeyholder(c))
