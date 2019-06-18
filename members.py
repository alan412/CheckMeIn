import csv
import sqlite3
import os
from collections import namedtuple
from enum import IntEnum

Member = namedtuple('Member', ['barcode', 'displayName', 'status'])


class Status(IntEnum):
    inactive = 0
    active = 1


class Members(object):
    def __init__(self, database):
        self.database = database

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version <= 2:
            dbConnection.execute(
                "ALTER TABLE members ADD COLUMN status INTEGER default 1")

    def addMemberDB(self, dbConnection, barcode, displayName, status):
        # will fail if it already exists
        dbConnection.execute("INSERT INTO members VALUES (?,?,?)",
                             (barcode, displayName, status))

    def loadFromCSV(self, filename, barcode, display):
        with sqlite3.connect(self.database) as c:
            c.execute('''CREATE TABLE members
                   (barcode TEXT UNIQUE, displayName TEXT, status INTEGER)''')

            with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.addMemberDB(
                        c, row[barcode], row[display], Status.active)

    def add(self, displayName, barcode):
        with sqlite3.connect(self.database) as c:
            data = c.execute(
                "SELECT displayName FROM members WHERE barcode==?", (barcode,)).fetchone()
            if data is None:
                self.addMemberDB(c, barcode, displayName, Status.active)
                return ''
            else:
                error = ''
                if data[0] != displayName:
                    error = "Barcode: " + barcode + \
                        " already in use by " + data[0]
        return error

    def getName(self, barcode):
        with sqlite3.connect(self.database) as c:
            data = c.execute(
                "SELECT displayName FROM members WHERE barcode==?", (barcode,)).fetchone()
            if data is None:
                return ('Invalid: ' + barcode, None)
            else:
                # Add code here for inactive
                return ('', data[0])

    def getBarcode(self, name, dbConnection=NULL):
        if not dbConnection:
            dbConnection = sqlite3.connect(self.database)

        with dbConnection as c:
            data = c.execute(
                "SELECT barcode FROM members WHERE displayName==?", (name,)).fetchone()
            if data is None:
                return ''
            else:
                # Add code here for inactive
                return data[0]

    def changeMemberStatus(self, newStatus, barcode):
        with sqlite3.connect(self.database) as c:
            c.execute('''UPDATE members
                       SET status = ?
                       WHERE (barcode==?)''',
                      (newStatus, barcode))

    def getList(self):
        memberList = []
        with sqlite3.connect(self.database) as c:
            for row in c.execute("SELECT * FROM members WHERE status is not ?", (Status.inactive,)):
                memberList.append(Member(row[0], row[1], row[2]))
        return memberList


# unit test
if __name__ == "__main__":  # pragma no cover
    DB_STRING = 'data/test.db'
    try:
        os.remove(DB_STRING)   # Start with a new one
    except IOError:
        pass  # Don't care if it didn't exist
    members = Members(DB_STRING)
    members.loadFromCSV('data/members.csv', 'TFI Barcode', 'TFI Display Name')
    for m in members.getList():
        print(m)

    members.changeMemberStatus(Status.inactive, "100091")

    for m in members.getList():
        print(m)
