from passlib.apps import custom_app_context as pwd_context
from enum import IntEnum
import time
import random
import datetime
import smtplib
import urllib
import email.utils
from email.mime.text import MIMEText


class Status(IntEnum):
    inactive = 0
    active = 1


class Role:
    COACH = 0x04
    SHOP_CERTIFIER = 0x08
    KEYHOLDER = 0x10
    ADMIN = 0x20

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
        if self.isCoach():
            roleStr += "Coach "
        return roleStr

    def __repr__(self):
        return str(self.value)


class Accounts(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):  # pragma: no cover
        if db_schema_version < 11:
            dbConnection.execute('''CREATE TABLE accounts
                                 (user TEXT PRIMARY KEY collate nocase,
                                  password TEXT,
                                  forgot TEXT,
                                  forgotTime TIMESTAMP,
                                  barcode TEXT UNIQUE,
                                  activeKeyholder INTEGER default 0,
                                  role INTEGER default 0)''')

    def addHashedUser(self, dbConnection, user, hashedPassword, barcode, role):
        dbConnection.execute(
            '''INSERT INTO accounts(user, password, barcode, role) VALUES(?,?,?,?)''',
            (user, hashedPassword, barcode, role.getValue()))

    def addUser(self, dbConnection, user, password, barcode, role):
        return self.addHashedUser(dbConnection, user, pwd_context.hash(password), barcode, role)

    def getBarcode(self, dbConnection, user, password):
        data = dbConnection.execute(
            '''SELECT password, barcode, role FROM accounts WHERE user = (?)''', (user,)).fetchone()
        if data is None:
            return ('', Role(0))
        if not pwd_context.verify(password, data[0]):
            return ('', Role(0))
        return (data[1], Role(data[2]))

    def getRole(self, dbConnection, barcode):
        data = dbConnection.execute(
            '''SELECT role FROM accounts WHERE barcode = (?)''', (barcode,)).fetchone()
        if data is None:
            return Role(0)
        return Role(data[0])

    def changePassword(self, dbConnection, user, oldPassword, newPassword):
        dbConnection.execute(
            '''UPDATE accounts SET password = ? WHERE (user = ?)''', (pwd_context.hash(newPassword), user))
        return True

    def emailToken(self, dbConnection, username, token):
        data = dbConnection.execute(
            '''SELECT email from accounts INNER JOIN members ON accounts.barcode = members.barcode WHERE user = ?''',
            (username, )).fetchone()
        emailAddress = data[0]

        safe_username = urllib.parse.quote_plus(username)
        msg = MIMEText("Please go to http://tfi.ev3hub.com/profile/resetPasswordToken?user=" + safe_username +
                       "&token=" + token + " to reset your password.  If you" +
                       " did not request that you had forgotten " +
                       "your password, then you can safely ignore this e-mail." +
                       " This expires in 24 hours.\n\nThank you,\nTFI")

        from_email = 'tfi@ev3hub.com'
        msg['To'] = email.utils.formataddr((username, emailAddress))
        msg['From'] = email.utils.formataddr(('TFI CheckMeIn', from_email))
        msg['Subject'] = 'Forgotten Password'

        try:  # pragma: no cover
            server = smtplib.SMTP('localhost')
            server.sendmail(from_email, [emailAddress], msg.as_string())
            server.quit()
        except IOError:
            print('Failed to send e-mail')
            print('Email would have been:', msg)
        return ''

    def forgotPassword(self, dbConnection, username):
        data = dbConnection.execute(
            '''SELECT forgotTime from accounts WHERE user = ?''', (username,)).fetchone()

        if data == None:
            return
        if data[0] != None:
            print(f'before subtract {data[0]}')
            longAgo = datetime.datetime.now() - data[0]
            print('after subtract')
            if longAgo.total_seconds() < 60:   # to keep people from spamming others...
                return
        chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
        forgotID = ''.join(random.SystemRandom().choice(chars)
                           for _ in range(8))

        dbConnection.execute(
            '''UPDATE accounts SET forgot = ?, forgotTime = ? WHERE user = ?''',
            (pwd_context.hash(forgotID), datetime.datetime.now(), username))

        self.emailToken(dbConnection, username, forgotID)

    def verify_forgot(self, dbConnection, username, forgot, newPassword):
        data = dbConnection.execute(
            '''SELECT forgot, forgotTime from accounts WHERE user = ?''', (username,)).fetchone()
        if not data:
            return False

        forgotTime = data[1]

        longAgo = datetime.datetime.now() - forgotTime
        if (longAgo.total_seconds() > 60*60*24):   # more than a day ago
            return False
        print(f'Forgot: {forgot}')
        if pwd_context.verify(forgot, data[0]):
            dbConnection.execute(
                '''UPDATE accounts SET forgot = ?, password = ? WHERE user = ?''',
                ('', pwd_context.hash(newPassword), username))
            return True
        print(f'Did not verify')
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

    def getNonAccounts(self, dbConnection):
        dictUsers = {}
        for row in dbConnection.execute('''SELECT members.barcode, displayName
            FROM members
            LEFT JOIN accounts USING (barcode)
            WHERE (user is NULL) AND (membershipExpires > ?)
            ORDER BY displayName''', (datetime.datetime.now(), )):
            dictUsers[row[0]] = row[1]
        return dictUsers

    def removeKeyholder(self, dbConnection):
        dbConnection.execute("UPDATE accounts SET activeKeyholder = ? WHERE (activeKeyholder==?)",
                             (Status.inactive, Status.active))

    def setActiveKeyholder(self, dbConnection, barcode):
        if barcode:
            self.removeKeyholder(dbConnection)
            dbConnection.execute(
                "UPDATE accounts SET activeKeyholder = ? WHERE (barcode==?) AND (role & ? != 0)", (Status.active, barcode, Role.KEYHOLDER))

    def getActiveKeyholder(self, dbConnection):
        """Returns the (barcode, name) of the active keyholder"""
        data = dbConnection.execute(
            '''SELECT accounts.barcode, displayName FROM accounts
               INNER JOIN members ON accounts.barcode = members.barcode
               WHERE activeKeyholder==?''', (Status.active,)).fetchone()
        if data is None:
            return ('', '')
        else:
            return (data[0], data[1])

    def getKeyholders(self, dbConnection):
        keyholders = []
        for row in dbConnection.execute('''SELECT user, barcode, password
            FROM accounts
            WHERE (role & ? != 0)''', (Role.KEYHOLDER, )):
            keyholders.append(
                {'user': row[0], 'barcode': row[1], 'password': row[2]})
        return keyholders

        # This is temporary - just to give us some fake data to play with
import sqlite3

if __name__ == '__main__':  # pragma: no cover
    with sqlite3.connect(
            'data/checkMeIn.db', detect_types=sqlite3.PARSE_DECLTYPES) as dbConnection:
        accounts = Accounts()

        accounts.addUser(dbConnection, 'alan', 'password',
                         '100091', Role(Role.ADMIN | Role.KEYHOLDER | Role.SHOP_CERTIFIER))
        accounts.addUser(dbConnection, 'abigail', 'password',
                         '100090', Role(Role.ADMIN))
        accounts.addUser(dbConnection, 'gsmith', 'password',
                         '100032', Role(Role.KEYHOLDER))
