import datetime


class Unlocks(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):  # pragma: no cover
        if db_schema_version < 11:
            dbConnection.execute('''CREATE TABLE unlocks
                                 (time TIMESTAMP,
                                  location TEXT,
                                  barcode TEXT)''')

    def addEntry(self, dbConnection, location, barcode):
        dbConnection.execute('''INSERT INTO unlocks(time, location, barcode) VALUES(?,?,?)''',
                             (datetime.datetime.now(), location, barcode))
