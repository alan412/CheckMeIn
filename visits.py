import datetime
import sqlite3
import os
from dateutil import parser
from members import Members
from guests import Guests
from reports import Reports
from teams import Teams
from keyholders import Keyholders
from customReports import CustomReports
from certifications import Certifications

SCHEMA_VERSION = 9


class Visits(object):
    def __init__(self, database):
        self.database = database
        self.members = Members()
        self.guests = Guests()
        self.keyholders = Keyholders()
        self.reports = Reports()
        self.teams = Teams()
        self.customReports = CustomReports(database)
        self.certifications = Certifications()
        if not os.path.exists(self.database):
            with self.dbConnect() as c:
                self.migrate(c, 0)
        else:
            with self.dbConnect() as c:
                data = c.execute('PRAGMA schema_version').fetchone()
                if data[0] != SCHEMA_VERSION:
                    self.migrate(c, data[0])

    def dbConnect(self):
        return sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version < SCHEMA_VERSION:
            # No change for Visits
            if db_schema_version == 0:
                dbConnection.execute('''CREATE TABLE visits
                     (start timestamp, leave timestamp, barcode text, status text)''')

            self.members.migrate(dbConnection, db_schema_version)
            self.guests.migrate(dbConnection, db_schema_version)
            self.keyholders.migrate(dbConnection, db_schema_version)
            self.teams.migrate(dbConnection, db_schema_version)
            self.customReports.migrate(dbConnection, db_schema_version)
            self.certifications.migrate(dbConnection, db_schema_version)
            dbConnection.execute(
                'PRAGMA schema_version = ' + str(SCHEMA_VERSION))
        elif db_schema_version != SCHEMA_VERSION:
            raise Exception("Unknown DB schema version" +
                            str(db_schema_version) + ": " + self.database)

    def enterGuest(self, dbConnection, guest_id):
        now = datetime.datetime.now()
        data = dbConnection.execute(
            "SELECT * FROM visits WHERE (barcode==?) and (status=='In')",
            (guest_id,)).fetchone()
        if data is None:
            dbConnection.execute("INSERT INTO visits VALUES (?,?,?,'In')",
                                 (now, now, guest_id))

    def leaveGuest(self, dbConnection, guest_id):
        now = datetime.datetime.now()
        dbConnection.execute(
            "UPDATE visits SET leave = ?, status = 'Out' WHERE (barcode==?) AND (status=='In')",
            (now, guest_id))

    def scannedMember(self, dbConnection, barcode):
        now = datetime.datetime.now()

        # See if it is a valid input
        data = dbConnection.execute(
            "SELECT displayName FROM members WHERE barcode==?", (barcode,)).fetchone()
        if data is None:
            return 'Invalid barcode: ' + barcode
        data = dbConnection.execute(
            "SELECT * FROM visits WHERE (barcode==?) and (status=='In')", (barcode,)).fetchone()
        if data is None:
            dbConnection.execute("INSERT INTO visits VALUES (?,?,?,'In')",
                                 (now, now, barcode))
            if not self.keyholders.getActiveKeyholder(dbConnection):
                self.keyholders.setActiveKeyholder(dbConnection, barcode)
        else:
            dbConnection.execute(
                "UPDATE visits SET leave = ?, status = 'Out' WHERE " +
                "(barcode==?) AND (status=='In')",
                (now, barcode))
        return ''

    def checkBuilding(self, dbConnection):
        now = datetime.datetime.now()
        if now.hour == 3 and self.reports.numberPresent() > 0:  # If between 3am and 4am
            self.emptyBuilding(dbConnection)

    def emptyBuilding(self, dbConnection):
        now = datetime.datetime.now()
        dbConnection.execute(
            "UPDATE visits SET leave = ?, status = 'Forgot' WHERE status=='In'", (now,))
        keyholder_barcode = self.getActiveKeyholder(dbConnection)
        if keyholder_barcode:
            dbConnection.execute(
                "UPDATE visits SET status = 'Out' WHERE barcode==? AND leave==?",
                (keyholder_barcode, now))
            self.keyholders.removeKeyholder(dbConnection)

    def oopsForgot(self, dbConnection):
        now = datetime.datetime.now()
        startDate = now.replace(hour=0, minute=0, second=0, microsecond=0)
        dbConnection.execute(
            "UPDATE visits SET status = 'In' WHERE status=='Forgot' AND leave > ?",
            (startDate,))

    def getKeyholderName(self, dbConnection):
        barcode = self.getActiveKeyholder(dbConnection)
        if barcode:
            (_, display) = self.members.getName(dbConnection, barcode)
            return display
        else:
            return 'N/A'

    def setActiveKeyholder(self, dbConnection, barcode):
        # TODO: once keyholders does verification, this should have the possibility of error
        leavingKeyholder = self.keyholders.getActiveKeyholder(dbConnection)
        self.keyholders.setActiveKeyholder(dbConnection, barcode)
        self.addIfNotHere(dbConnection, barcode)
        if leavingKeyholder:
            self.scannedMember(dbConnection, leavingKeyholder)
        return ''

    def getMembersInBuilding(self, dbConnection):
        listPresent = []
        for row in dbConnection.execute('''SELECT displayName, visits.barcode
            FROM visits
            INNER JOIN members ON members.barcode = visits.barcode
            WHERE visits.status=='In'
            ORDER BY displayName'''):
            listPresent.append([row[0], row[1]])
        return listPresent

    def getAllMembers(self):
        listPresent = []
        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            for row in c.execute('''SELECT displayName, barcode FROM members ORDER BY displayName'''):
                listPresent.append([row[0], row[1]])
        return listPresent

    def getMemberBarcodesInBuilding(self, dbConnection):
        listPresent = []

        for row in dbConnection.execute('''SELECT visits.barcode
                FROM visits
                INNER JOIN members ON members.barcode = visits.barcode
                WHERE visits.status=='In' ORDER BY displayName'''):
            listPresent.append(row[0])
        return listPresent

    def getActiveKeyholder(self, dbConnection):
        return self.keyholders.getActiveKeyholder(dbConnection)

    def addIfNotHere(self, dbConnection, barcode):
        now = datetime.datetime.now()
        dbConnection.execute('''INSERT INTO visits (START,LEAVE,BARCODE,STATUS)
                      SELECT ?,?,?,'In'
                      WHERE NOT EXISTS(
                          SELECT 1 FROM visits
                          WHERE ((barcode==?) and (status=='In')))''',
                             (now, now, barcode, barcode))

    def fix(self, dbConnection, fixData):
        entries = fixData.split(',')

        for entry in entries:
            tokens = entry.split('!')
            if len(tokens) == 3:
                rowID = tokens[0]
                newStart = parser.parse(tokens[1])
                newLeave = parser.parse(tokens[2])

                # if crossed over midnight....
                if newLeave < newStart:
                    newLeave += datetime.timedelta(days=1)

                dbConnection.execute('''UPDATE visits SET start = ?, leave = ?, status = 'Out'
                        WHERE (visits.rowid==?)''', (newStart, newLeave, rowID))


# unit test

def testOutput(dbConnection, testNum, test):  # pragma no cover
    result = test
    if result:
        print("Result: ", result)
    print(testNum, visits.reports.whoIsHere(dbConnection))


class TestFile():
    def __init__(self, filename):
        self.file = open(filename, "rb")
        self.filename = filename


if __name__ == "__main__":  # pragma no cover
    DB_STRING = 'data/test.db'
    try:
        os.remove(DB_STRING)   # Start with a new one
    except IOError:
        pass  # Don't care if it didn't exist

    visits = Visits(DB_STRING)
    dbConnection = sqlite3.connect(
        DB_STRING, detect_types=sqlite3.PARSE_DECLTYPES)
    visits.members.bulkAdd(dbConnection, TestFile("data/members.csv"))
    testOutput(dbConnection, 1, '')
    testOutput(dbConnection, 2, visits.scannedMember(dbConnection, '100091'))
    testOutput(dbConnection, 3, visits.scannedMember(dbConnection, '100090'))
    testOutput(dbConnection, 4, visits.scannedMember(dbConnection, '100090'))
    gid = visits.guests.add(dbConnection,
                            "Test 1", "Test", "1", "noemail@domain.com", "", False)
    testOutput(dbConnection, 5, visits.enterGuest(dbConnection, gid))
    testOutput(dbConnection, 6, visits.leaveGuest(dbConnection, gid))
    testOutput(dbConnection, 7, visits.scannedMember(dbConnection, '100091'))
    testOutput(dbConnection, 8, visits.addIfNotHere(dbConnection, '100091'))
    testOutput(dbConnection, 9, visits.addIfNotHere(dbConnection, '100091'))
    testOutput(dbConnection, 10, visits.emptyBuilding(dbConnection))
