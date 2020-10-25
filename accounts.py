from passlib.apps import custom_app_context as pwd_context
from enum import IntEnum
import time
import random
import datetime


class Role:
    KEYHOLDER = 0x10
    ADMIN = 0x20

    def __init__(self, value=0):
        self.value = value

    def isKeyholder(self):
        return self.value & self.KEYHOLDER

    def isAdmin(self):
        return self.value & self.ADMIN

    def setValue(self, check, value):
        if type(check) == str:
            check = int(check)
        self.value = (self.value | value) if check else (self.value & ~value)

    def setKeyholder(self, keyholder):
        self.setValue(keyholder, self.KEYHOLDER)

    def setAdmin(self, admin):
        self.setValue(admin, self.ADMIN)

    def getValue(self):
        return self.value

    def __str__(self):
        roleStr = ""
        if self.isAdmin():
            roleStr += "Admin "
        if self.isKeyholder():
            roleStr += "Keyholder "
        return roleStr


class Accounts(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):  # pragma: no cover
        if db_schema_version < 11:
            dbConnection.execute('''CREATE TABLE accounts
                                 (user TEXT PRIMARY KEY,
                                  password TEXT,
                                  forgot TEXT,
                                  forgotTime DATETIME,
                                  barcode TEXT UNIQUE,
                                  role INTEGER default 0)''')

    def addUser(self, dbConnection, user, password, barcode, role):
        dbConnection.execute(
            '''INSERT INTO accounts(user, password, barcode, role) VALUES(?,?,?,?)''',
            (user, pwd_context.hash(password), barcode, role.getValue()))

    def getAdminBarcode(self, dbConnection, user, password):
        print(f"User: {user}")
        data = dbConnection.execute(
            '''SELECT password, barcode, role FROM accounts WHERE user = (?)''', (user,)).fetchone()
        if data is None:
            return ''
        print(f"Data: {data}")
        if not pwd_context.verify(password, data[0]):
            return ''
        if not Role(data[2]).isAdmin():
            return ''
        return data[1]

    def changePassword(self, dbConnection, user, oldPassword, newPassword):
        dbConnection.execute(
            '''UPDATE accounts SET password = ? WHERE (user = ?)''', (pwd_context.hash(newPassword), user))
        return True

    def emailToken(self, dbConnection, username, token):
        data = dbConnection.execute(
            '''SELECT email from accounts INNER JOIN members ON accounts.barcode = members.barcode WHERE username = ?''',
            (username, )).fetchone()
        email = data[0]
        print("********* TOKEN EMAIL NOT IMPLEMENTED YET ************")
        print(f"Token: {token} to {email}")

    def forgotPassword(self, dbConnection, username):
        data = dbConnection.execute(
            '''SELECT forgotTime from accounts WHERE username = ?''', (username,))
        longAgo = datetime.datetime.now - data[0]
        if longAgo.total_seconds() < 60:   # to keep people from spamming others...
            return

        chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
        forgotID = ''.join(random.SystemRandom().choice(chars)
                           for _ in range(8))

        dbConnection.execute(
            '''UPDATE accounts SET forgot = ?, forgotTime = ? WHERE username = ?''',
            (pwd_context.hash(forgotID), datetime.datetime.now(), username))

        emailToken(dbConnection, username, forgotID)

    def verify_forgot(self, username, forgot, newPassword):
        data = dbConnection.execute(
            '''SELECT forgot, forgotTime from accounts WHERE username = ?''', (username,)).fetchone()
        forgotTime = data[1]

        longAgo = datetime.datetime.now() - forgotTime
        if (longAgo.total_seconds() > 60*60*24):   # more than a day ago
            return False
        if pwd_context.verify(forgot, data[0]):
            dbConnection.execute(
                '''UPDATE acccounts SET forgot = ?, password = ? WHERE username = ?''',
                ('', pwd_context.hash(newPassword), username))
            return True
        return False

    def changeRole(self, dbConnection, barcode, newRole):
        dbConnection.execute(
            '''UPDATE accounts SET role = ? WHERE (barcode = ?)''', (newRole.getValue(), barcode))

    def removeUser(self, dbConnection, barcode):
        dbConnection.execute(
            '''DELETE from accounts WHERE barcode= ?''', (barcode,))

    def getUsers(self, dbConnection):
        dictUsers = {}
        for row in dbConnection.execute('''SELECT user, accounts.barcode, role, displayName
            FROM accounts
            INNER JOIN members ON members.barcode = accounts.barcode
            ORDER BY user'''):
            dictUsers[row[0]] = {'barcode': row[1],
                                 'role': Role(row[2]), 'displayName': row[3]}
        return dictUsers


# This is temporary - just to give us some fake data to play with
import sqlite3

if __name__ == '__main__':  # pragma: no cover
    with sqlite3.connect(
            'data/checkMeIn.db', detect_types=sqlite3.PARSE_DECLTYPES) as dbConnection:
        accounts = Accounts()

        accounts.addUser(dbConnection, 'alan', 'password',
                         '100091', Role(Role.ADMIN | Role.KEYHOLDER))
        accounts.addUser(dbConnection, 'abigail', 'password',
                         '100090', Role(Role.ADMIN))
        accounts.addUser(dbConnection, 'gsmith', 'password',
                         '100032', Role(Role.KEYHOLDER))
