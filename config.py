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
            self.update(dbConnection, datum["key"], datum["value"])

    def update(self, dbConnection, key, value):
        dbConnection.execute(
            "INSERT into config(key, value) values(?, ?) on conflict(key) do update set value = ?",
            (key, value, value)
        )

    def get(self, dbConnection, key):
        row = dbConnection.execute(
            "SELECT value from config WHERE (key=?)", (key, )).fetchone()
        return row and row[0]
