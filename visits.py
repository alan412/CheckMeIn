import datetime
import sqlite3
import os
from dateutil import parser
from members import Members
from guests import Guests
from reports import Reports
from teams import Teams
from customReports import CustomReports
from certifications import Certifications


class Visits(object):
    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version == 0:
            dbConnection.execute('''CREATE TABLE visits
                     (start timestamp, leave timestamp, barcode text, status text)'''
                                 )

    def injectData(self, dbConnection, data):
        for datum in data:
            if "leave" in datum:
                dbConnection.execute("INSERT INTO visits VALUES (?,?,?,?)",
                                     (datum["start"], datum["leave"],
                                      datum["barcode"], datum["status"]))
            else:
                dbConnection.execute("INSERT INTO visits VALUES (?,?,?,?)",
                                     (datum["start"], datum["start"],
                                      datum["barcode"], datum["status"]))

    def inBuilding(self, dbConnection, barcode):
        data = dbConnection.execute(
            "SELECT * FROM visits WHERE (barcode==?) and (status=='In')",
            (barcode, )).fetchone()
        return data != None

    def enterGuest(self, dbConnection, guest_id):
        now = datetime.datetime.now()
        dbConnection.execute('''
            INSERT INTO visits(start, leave, barcode, status) 
            SELECT ?, ?, ?, 'In'
            WHERE NOT EXISTS (SELECT 1 FROM visits WHERE (barcode == ?) AND (status == 'In'))''',
                             (now, now, guest_id, guest_id))

    def leaveGuest(self, dbConnection, guest_id):
        now = datetime.datetime.now()
        dbConnection.execute(
            "UPDATE visits SET leave = ?, status = 'Out' WHERE (barcode==?) AND (status=='In')",
            (now, guest_id))

    def checkInMember(self, dbConnection, barcode):
        # For now members and guests are the same
        return self.enterGuest(dbConnection, barcode)

    def checkOutMember(self, dbConnection, barcode):
        # For now members and guests are the same
        return self.leaveGuest(dbConnection, barcode)

    def scannedMember(self, dbConnection, barcode):
        now = datetime.datetime.now()

        # See if it is a valid input
        data = dbConnection.execute(
            "SELECT displayName FROM members WHERE barcode==?",
            (barcode, )).fetchone()
        if data is None:
            return 'Invalid barcode: ' + barcode
        data = dbConnection.execute(
            "SELECT * FROM visits WHERE (barcode==?) and (status=='In')",
            (barcode, )).fetchone()
        if data is None:
            dbConnection.execute("INSERT INTO visits VALUES (?,?,?,'In')",
                                 (now, now, barcode))
        else:
            dbConnection.execute(
                "UPDATE visits SET leave = ?, status = 'Out' WHERE " +
                "(barcode==?) AND (status=='In')", (now, barcode))
        return ''

    def emptyBuilding(self, dbConnection, keyholder_barcode):
        now = datetime.datetime.now()
        dbConnection.execute(
            "UPDATE visits SET leave = ?, status = 'Forgot' WHERE status=='In'",
            (now, ))
        if keyholder_barcode:
            dbConnection.execute(
                "UPDATE visits SET status = 'Out' WHERE barcode==? AND leave==?",
                (keyholder_barcode, now))

    def oopsForgot(self, dbConnection):
        now = datetime.datetime.now()
        startDate = now.replace(hour=0, minute=0, second=0, microsecond=0)
        dbConnection.execute(
            "UPDATE visits SET status = 'In' WHERE status=='Forgot' AND leave > ?",
            (startDate, ))

    def getMembersInBuilding(self, dbConnection):
        listPresent = []
        for row in dbConnection.execute('''SELECT displayName, visits.barcode
            FROM visits
            INNER JOIN members ON members.barcode = visits.barcode
            WHERE visits.status=='In'
            ORDER BY displayName'''):
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

                dbConnection.execute(
                    '''UPDATE visits SET start = ?, leave = ?, status = 'Out'
                        WHERE (visits.rowid==?)''',
                    (newStart, newLeave, rowID))
