import csv
import sqlite3
import os
import codecs
import datetime


class Members(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):   # pragma: no cover
        if db_schema_version == 0:
            dbConnection.execute('''
                CREATE TABLE members (barcode TEXT UNIQUE,
                                      displayName TEXT)
            ''')

        if db_schema_version <= 8:
            past = datetime.datetime.now() - datetime.timedelta(-90)
            # default is expires in 90 days
            future = datetime.datetime.now() + datetime.timedelta(90)
            dbConnection.execute(
                '''
                CREATE TABLE new_members (barcode TEXT UNIQUE,
                                          displayName TEXT,
                                          firstName TEXT,
                                          lastName TEXT,
                                          email TEXT,
                                          membershipExpires TIMESTAMP)
                ''')
            for row in dbConnection.execute("SELECT * FROM members"):
                dbConnection.execute('''
                INSERT INTO new_members VALUES (?,?,'','','',?)''',
                                     (row[0], row[1], future if row[2] else past))
            dbConnection.execute('''DROP TABLE members''')
            dbConnection.execute(
                '''ALTER TABLE new_members RENAME TO members''')

    def bulkAdd(self, dbConnection, csvFile):
        numMembers = 0
        for row in csv.DictReader(codecs.iterdecode(csvFile.file, 'utf-8')):
            displayName = row['TFI Display Name for Button']
            if not displayName:
                displayName = row['First Name'] + ' ' + row['Last Name'][0]
            barcode = row['TFI Barcode for Button']
            if not barcode:
                barcode = row['TFI Barcode AUTONUM']
            try:
                email = row['Email']
            except KeyError:
                email = ''
            try:
                (month, day, year) = row['Membership End Date'].split("/")
            except ValueError:
                (month, day, year) = (6, 30, 2019)

            membershipExpires = datetime.datetime(
                year=int(year), month=int(month), day=int(day))

            # This is because I can't figure our how to get the ubuntu to use
            # the newer version of sqlite3.  At some point this should go back
            # to the commit before this one.   Arrggghhhh.
            try:
                data = dbConnection.execute('''
                INSERT INTO MEMBERS(barcode, displayName, firstName, lastName, email, membershipExpires) 
                VALUES (?,?,?,?,?,?)''',
                                            (barcode, displayName, row['First Name'], row['Last Name'], email, membershipExpires))
            except sqlite3.IntegrityError:
                data = dbConnection.execute('''
                UPDATE MEMBERS SET
                displayName = ?,
                firstName = ?,
                lastName = ?,
                email = ?,
                membershipExpires = ?
                WHERE barcode=?''',
                                            (displayName, row['First Name'], row['Last Name'], email, membershipExpires, barcode))

#               ON CONFLICT(barcode)
#               DO UPDATE SET
#                   displayName=excluded.displayName,
#                   firstName=excluded.firstName,
#                   lastName=excluded.lastName,
#                   email=excluded.email,
#                   membershipExpires=excluded.membershipExpires
#               ''',
            numMembers = numMembers + 1

        return f"Imported {numMembers} from {csvFile.filename}"

    def getActive(self, dbConnection):
        listUsers = []
        for row in dbConnection.execute('''SELECT displayName, barcode
            FROM members
            WHERE (membershipExpires > ?)
            ORDER BY displayName''', (datetime.datetime.now(), )):
            listUsers.append([row[0], row[1]])
        return listUsers

# TODO: should this check for inactive?
    def getName(self, dbConnection, barcode):
        data = dbConnection.execute(
            "SELECT displayName FROM members WHERE barcode==?", (barcode,)).fetchone()
        if data is None:
            return ('Invalid: ' + barcode, None)
        else:
            # Add code here for inactive
            return ('', data[0])
