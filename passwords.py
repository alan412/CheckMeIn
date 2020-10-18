from passlib.apps import custom_app_context as pwd_context
from enum import IntEnum


class Role(IntEnum):
    none = 0
    keyholder = 10
    admin = 20  # Admin by definition is also a keyholder


class Passwords(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):  # pragma: no cover
        if db_schema_version < 11:
            dbConnection.execute('''CREATE TABLE passwords
                                 (user TEXT PRIMARY KEY,
                                  password TEXT,
                                  barcode TEXT,
                                  role INTEGER default 0)''')

    def addUser(self, dbConnection, user, password, barcode, role):
        dbConnection.execute(
            '''INSERT INTO passwords(user, password, barcode, role) VALUES(?,?,?,?)''',
            (user, pwd_context.hash(password), barcode, role))

    def getBarcode(self, dbConnection, user, password, minRole=0):
        print(f"User: {user}")
        data = dbConnection.execute(
            '''SELECT password, barcode, role FROM passwords WHERE user = (?)''', (user,)).fetchone()
        if data is None:
            return ''
        print(f"Data: {data}")
        if not pwd_context.verify(password, data[0]):
            return ''
        if data[2] < minRole:
            return ''
        return data[1]

    def changePassword(self, dbConnection, user, password):
        barcode = self.getBarcode(dbConnection, user, password)
        if barcode:
            dbConnection.execute(
                '''UPDATE passwords SET password = ? WHERE (user = ?)''', (pwd_context.hash(password), user))
            return True
        return False

    def removeUser(self, dbConnection, user):
        dbConnection.execute(
            '''DELETE from passwords WHERE user= ?''', (user,))
