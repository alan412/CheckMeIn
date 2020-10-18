
class Devices(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):  # pragma: no cover
        if db_schema_version < 11:
            dbConnection.execute('''CREATE TABLE devices
                                 (mac TEXT PRIMARY KEY,
                                  name TEXT,
                                  barcode TEXT)''')
    def addDevice(self, dbConnection, mac, name, barcode):
        dbConnection.execute("INSERT INTO devices(mac, name, barcode) VALUES(?,?,?)",(mac,name, barcode))
    
    def delDevice(self, dbConnection, mac):
        dbConnection.execute("DELETE from devices WHERE (mac=?)", (mac,))
    
    def changeDevice(self, dbConnection, oldMAC, newMAC):
        dbConnection.execute("UPDATE devices SET (mac=?) WHERE (mac=?)", (oldMAC, newMAC))