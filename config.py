class Config(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version < 14:
            dbConnection.execute('''CREATE TABLE config
                                 (key TEXT PRIMARY KEY,
                                  value TEXT)''')
            dbConnection.execute(
                '''INSERT INTO config(key,value) VALUES('grace_period', '90')''')

    def injectData(self, dbConnection, data):
        for datum in data:
            self.add(dbConnection, datum["key"], datum["value"])

    def add(self, dbConnection, key, value):
        dbConnection.execute(
            "INSERT INTO config(key, value) VALUES(?,?)",
            (key, value))

    def updateOrAdd(self, dbConnection, key, value):
        dbConnection.execute(
            "INSERT into config(key, value) values(?, ?) on conflict(key) do update set value = ?",
            (key, value, value)
        )

    def delete(self, dbConnection, key):
        dbConnection.execute(
            "DELETE from config WHERE (key=?)",
            (key, ))

    def get(self, dbConnection, key):
        row = dbConnection.fetchone(
            "SELECT value from config WHERE (key=?)", (key, ))
        return row and row[0]

    def getConfigDict(self, dbConnection):
        configDict = {}
        for row in dbConnection.execute(
                "SELECT key, value from CONFIG"):
            configDict[row[0]] = row[1]
        return configDict
