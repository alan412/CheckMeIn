import sqlite3
from passlib.apps import custom_app_context as pwd_context
from enum import IntEnum
import time
import random
import datetime
import urllib
import utils
import sys


class Status(IntEnum):
    inactive = 0
    active = 1


class Role:
    COACH = 0x04
    SHOP_CERTIFIER = 0x08
    KEYHOLDER = 0x10
    ADMIN = 0x20
    SHOP_STEWARD = 0x40

    def __init__(self, value=0):
        self.value = value

    def isRole(self, role):
        return self.value & role

    def isKeyholder(self):
        return self.isRole(self.KEYHOLDER)

    def isAdmin(self):
        return self.isRole(self.ADMIN)

    def isShopCertifier(self):
        return self.isRole(self.SHOP_CERTIFIER)

    def isCoach(self):
        return self.isRole(self.COACH)

    def isShopSteward(self):
        return self.isRole(self.SHOP_STEWARD)

    def setValue(self, check, value):
        if type(check) == str:
            check = int(check)
        self.value = (self.value | value) if check else (self.value & ~value)

    def setKeyholder(self, keyholder):
        self.setValue(keyholder, self.KEYHOLDER)

    def setAdmin(self, admin):
        self.setValue(admin, self.ADMIN)

    def setShopCertifier(self, admin):
        self.setValue(admin, self.SHOP_CERTIFIER)

    def setCoach(self, coach):
        self.setValue(coach, self.COACH)

    def setShopSteward(self, steward):
        self.setValue(steward, self.SHOP_STEWARD)

    def getValue(self):
        return self.value

    def __str__(self):
        roleStr = ""
        if self.isAdmin():
            roleStr += "Admin "
        if self.isKeyholder():
            roleStr += "Keyholder "
        if self.isShopCertifier():
            roleStr += "Certifier "
        if self.isShopSteward():
            roleStr += "Steward "
        if self.isCoach():
            roleStr += "Coach "

        return roleStr

    def __repr__(self):
        return str(self.value)


class Accounts(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version < 11:
            dbConnection.execute('''CREATE TABLE accounts
                                 (user TEXT PRIMARY KEY collate nocase,
                                  password TEXT,
                                  forgot TEXT,
                                  forgotTime TIMESTAMP,
                                  barcode TEXT UNIQUE,
                                  activeKeyholder INTEGER default 0,
                                  role INTEGER default 0)''')

    def injectData(self, dbConnection, data):
        for datum in data:
            self.addUser(dbConnection, datum["user"], datum["password"],
                         datum["barcode"], Role(datum["role"]))

    def addUser(self, dbConnection, user, password, barcode, role):
        hashedPassword = pwd_context.hash(password)
        dbConnection.execute(
            '''INSERT INTO accounts(user, password, barcode, role) VALUES(?,?,?,?)''',
            (user, hashedPassword, barcode, role.getValue()))
        emailAddress = self.getEmail(dbConnection, user)

        utils.sendEmail('TFI Ops', 'tfi-ops@googlegroups.com', 'New User',
                        f'User {user} <{emailAddress}> added with roles : {role}')

    def getBarcode(self, dbConnection, user, password):
        data = dbConnection.execute(
            '''SELECT password, barcode, role FROM accounts WHERE user = (?)''',
            (user, )).fetchone()
        if data is None:
            return ('', Role(0))
        if not pwd_context.verify(password, data[0]):
            return ('', Role(0))
        return (data[1], Role(data[2]))

    def getMembersWithRole(self, dbConnection, role):
        listUsers = []
        for row in dbConnection.execute(
                '''SELECT displayName, accounts.barcode
            FROM accounts
            INNER JOIN v_current_members ON (v_current_members.barcode = accounts.barcode)
            WHERE (role & ? != 0)
            ORDER BY displayName''', (role, )):
            listUsers.append([row[0], row[1]])
        return listUsers

    def getPresentWithRole(self, dbConnection, role):
        listUsers = []
        for row in dbConnection.execute(
                '''SELECT displayName, accounts.barcode
            FROM accounts
            INNER JOIN v_current_members ON (v_current_members.barcode = accounts.barcode)
            INNER JOIN visits ON (visits.barcode = accounts.barcode)
            WHERE visits.status = "In" AND (role & ? != 0)
            ORDER BY displayName''', (role, )):
            listUsers.append([row[0], row[1]])
        return listUsers

    def changePassword(self, dbConnection, user, oldPassword, newPassword):
        dbConnection.execute(
            '''UPDATE accounts SET password = ? WHERE (user = ?)''',
            (pwd_context.hash(newPassword), user))
        return True

    def getEmail(self, dbConnection, username):
        data = dbConnection.execute(
            '''SELECT email from accounts INNER JOIN members ON accounts.barcode = members.barcode WHERE user = ?''',
            (username, )).fetchone()
        return data[0]

    def getUser(self, dbConnection, email):
        data = dbConnection.execute(
            '''SELECT user from accounts INNER JOIN members ON accounts.barcode = members.barcode WHERE email = ?''',
            (email, )).fetchone()
        if data:
            return data[0]
        return None

    def emailToken(self, dbConnection, username, token):
        emailAddress = self.getEmail(dbConnection, username)

        safe_username = urllib.parse.quote_plus(username)
        print(safe_username, token)

        msg = "Please go to http://tfi.checkmein.site/profile/resetPasswordToken?user=" + \
            safe_username + "&token=" + token + " to reset your password.  If you" + \
            " did not request that you had forgotten " + \
            "your password, then you can safely ignore this e-mail." + \
            "Your username is " + safe_username + "." + \
            " This expires in 24 hours.\n\nThank you,\nTFI"

        utils.sendEmail(username, emailAddress, 'Forgotten Password', msg)

        return emailAddress

    def forgotPassword(self, dbConnection, username):
        data = dbConnection.execute(
            '''SELECT forgotTime from accounts WHERE user = ?''',
            (username, )).fetchone()
        if data == None:
            username = self.getUser(dbConnection, username)
            data = dbConnection.execute(
                '''SELECT forgotTime from accounts WHERE user = ?''',
                (username, )).fetchone()
        if data == None:
            return f'No email sent due to not finding user: {username}'
        if data[0] != None:
            longAgo = datetime.datetime.now() - data[0]
            if longAgo.total_seconds() < 60:  # to keep people from spamming others...
                return 'No email sent due to one sent in last minute'
        chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
        forgotID = ''.join(random.SystemRandom().choice(chars)
                           for _ in range(8))

        dbConnection.execute(
            '''UPDATE accounts SET forgot = ?, forgotTime = ? WHERE user = ?''',
            (pwd_context.hash(forgotID), datetime.datetime.now(), username))
        return self.emailToken(dbConnection, username, forgotID)

    def verify_forgot(self, dbConnection, username, forgot, newPassword):
        data = dbConnection.execute(
            '''SELECT forgot, forgotTime from accounts WHERE user = ?''',
            (username, )).fetchone()
        if not data:
            return False

        forgotTime = data[1]

        longAgo = datetime.datetime.now() - forgotTime
        if (longAgo.total_seconds() > 60 * 60 * 24):  # more than a day ago
            return False
        if pwd_context.verify(forgot, data[0]):
            dbConnection.execute(
                '''UPDATE accounts SET forgot = ?, password = ? WHERE user = ?''',
                ('', pwd_context.hash(newPassword), username))
            return True
        return False

    def changeRole(self, dbConnection, barcode, newRole):
        dbConnection.execute(
            '''UPDATE accounts SET role = ? WHERE (barcode = ?)''',
            (newRole.getValue(), barcode))
        data = dbConnection.execute(
            '''SELECT user FROM accounts WHERE barcode = ?''',
            (barcode, )).fetchone()
        if data:
            emailAddress = self.getEmail(dbConnection, data[0])
            utils.sendEmail('TFI Ops', 'tfi-ops@googlegroups.com', 'Role change for user',
                            f'User {data[0]} <{emailAddress}> roles changed to : {newRole}')

    def removeUser(self, dbConnection, barcode):
        dbConnection.execute('''DELETE from accounts WHERE barcode= ?''',
                             (barcode, ))

    def getUsers(self, dbConnection):
        dictUsers = {}
        for row in dbConnection.execute(
                '''SELECT user, accounts.barcode, role, displayName
            FROM accounts
            INNER JOIN members ON members.barcode = accounts.barcode
            ORDER BY user'''):
            dictUsers[row[0]] = {
                'barcode': row[1],
                'role': Role(row[2]),
                'displayName': row[3]
            }
        return dictUsers

    def getNonAccounts(self, dbConnection):
        dictUsers = {}
        for row in dbConnection.execute(
                '''SELECT v_current_members.barcode, displayName
            FROM v_current_members
            LEFT JOIN accounts USING (barcode)
            WHERE (user is NULL) 
            ORDER BY displayName'''):
            dictUsers[row[0]] = row[1]
        return dictUsers

    def removeKeyholder(self, dbConnection):
        dbConnection.execute(
            "UPDATE accounts SET activeKeyholder = ? WHERE (activeKeyholder==?)",
            (Status.inactive, Status.active))

    def setActiveKeyholder(self, dbConnection, barcode):
        returnValue = False
        # If current barcode is a keyholder
        if barcode:
            (keyholderBarcode, _) = self.getActiveKeyholder(dbConnection)
            if barcode != keyholderBarcode:
                dbConnection.execute(
                    "UPDATE accounts SET activeKeyholder = ? WHERE (barcode==?) AND (role & ? != 0)",
                    (Status.active, barcode, Role.KEYHOLDER))
                data = dbConnection.execute('SELECT changes();').fetchone()
                if data and data[0]:   # There were changes from the last update statement
                    returnValue = True
                    if keyholderBarcode:
                        dbConnection.execute(
                            '''UPDATE accounts SET activeKeyholder = ? WHERE (barcode==?) AND changes() > 0''',
                            (Status.inactive, keyholderBarcode)
                        )
        return returnValue

    def getActiveKeyholder(self, dbConnection):
        """Returns the (barcode, name) of the active keyholder"""
        data = dbConnection.execute(
            '''SELECT accounts.barcode, displayName FROM accounts
               INNER JOIN members ON accounts.barcode = members.barcode
               WHERE activeKeyholder==?''', (Status.active, )).fetchone()
        if data is None:
            return ('', '')
        else:
            return (data[0], data[1])

    def getKeyholders(self, dbConnection):
        keyholders = []
        for row in dbConnection.execute(
                '''SELECT user, barcode, password
            FROM accounts
            WHERE (role & ? != 0)''', (Role.KEYHOLDER, )):
            keyholders.append({
                'user': row[0],
                'barcode': row[1],
                'password': row[2]
            })
        return keyholders

    def getKeyholderBarcodes(self, dbConnection):
        keyholders = []
        for row in dbConnection.execute(
                '''SELECT barcode
            FROM accounts
            WHERE (role & ? != 0)''', (Role.KEYHOLDER, )):
            keyholders.append(row[0])

        return keyholders
