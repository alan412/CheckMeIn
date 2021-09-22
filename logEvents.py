import datetime


class LogEvents(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version <= 12:
            dbConnection.execute('''
                CREATE TABLE logEvents (what TEXT,
                                        date TIMESTAMP,
                                        barcode TEXT)
            ''')

    def injectData(self, dbConnection, data):
        for datum in data:
            self.addEvent(
                dbConnection, datum["what"], datum["barcode"], datum["date"])

    def addEvent(self, dbConnection, what, barcode, date=None):
        if not date:
            date = datetime.datetime.now()

        dbConnection.execute("INSERT INTO logEvents VALUES (?,?,?)",
                             (what, date, barcode))

    def getLastEvent(self, dbConnection, what):
        data = dbConnection.execute(
            '''SELECT date, barcode from logEvents WHERE what = ? ORDER BY date DESC LIMIT 1''', (what,)).fetchone()
        if data:
            return (data[0], data[1])
        return (None, None)
