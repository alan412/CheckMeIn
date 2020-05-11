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

class Visits(object):
    def migrate(self, dbConnection, db_schema_version):  #pragma: no cover
        if db_schema_version == 0:
            dbConnection.execute('''CREATE TABLE visits
                     (start timestamp, leave timestamp, barcode text, status text)''')

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

    def emptyBuilding(self, dbConnection, keyholder_barcode):
        now = datetime.datetime.now()
        dbConnection.execute(
            "UPDATE visits SET leave = ?, status = 'Forgot' WHERE status=='In'", (now,))
        if keyholder_barcode:
            dbConnection.execute(
                "UPDATE visits SET status = 'Out' WHERE barcode==? AND leave==?",
                (keyholder_barcode, now))

    def oopsForgot(self, dbConnection):
        now = datetime.datetime.now()
        startDate = now.replace(hour=0, minute=0, second=0, microsecond=0)
        dbConnection.execute(
            "UPDATE visits SET status = 'In' WHERE status=='Forgot' AND leave > ?",
            (startDate,))

    def getMembersInBuilding(self, dbConnection):
        listPresent = []
        for row in dbConnection.execute('''SELECT displayName, visits.barcode
            FROM visits
            INNER JOIN members ON members.barcode = visits.barcode
            WHERE visits.status=='In'
            ORDER BY displayName'''):
            listPresent.append([row[0], row[1]])
        return listPresent

    def getAllMembers(self, dbConnection):
        listPresent = []
        for row in dbConnection.execute('''SELECT displayName, barcode FROM members ORDER BY displayName'''):
                listPresent.append([row[0], row[1]])
        return listPresent

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
