import sqlite3
import os
import csv
import members
from enum import IntEnum


class CertificationLevels(IntEnum):
    none = 0
    basic = 1
    certified = 10
    dof = 20
    instructor = 30
    certifier = 40


class Certifications(object):
    def __init__(self, database):
        self.database = database

    def createTable(self):
        with sqlite3.connect(self.database) as c:
            self.migrate(c, 0)

    def addTool(self, dbConnection, tool_id, grouping, name, restriction=0, comments=''):
        dbConnection.execute('INSERT INTO tools VALUES(?,?,?,?,?)',
                             (tool_id, grouping, name, restriction, comments))

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version < 8:
            dbConnection.execute('''CREATE TABLE restrictions
                                    (id        INTEGER PRIMARY KEY,
                                     descr     TEXT)''')
            dbConnection.execute('''INSERT INTO restrictions VALUES(
                                1, "Over 18 Only")''')

            dbConnection.execute('''CREATE TABLE tools
                                 (id           INTEGER PRIMARY KEY,
                                  grouping     TEXT,
                                  name         TEXT,
                                  restriction  INTEGER DEFAULT 0,
                                  comments     TEXT)''')

            self.addTool(dbConnection, 1, 1, "Sheet Metal Brake")
            self.addTool(dbConnection, 2, 1, "Blind Rivet Gun")
            self.addTool(dbConnection, 3, 1, "Stretcher Shrinker")
            self.addTool(dbConnection, 4, 1, "3D printers")

            self.addTool(dbConnection, 5, 2, "Power Hand Drill")
            self.addTool(dbConnection, 6, 2, "Solder Iron")
            self.addTool(dbConnection, 7, 2, "Dremel")

            self.addTool(dbConnection, 8, 3, "Horizontal Band Saw")
            self.addTool(dbConnection, 9, 3, "Drill Press")
            self.addTool(dbConnection, 10, 3, "Grinder / Sander")

            self.addTool(dbConnection, 11, 4, "Scroll Saw")
            self.addTool(dbConnection, 12, 4, "Table Mounted Jig Saw")
            self.addTool(dbConnection, 13, 4, "Vertical Band Saw")
            self.addTool(dbConnection, 14, 4, "Jig Saw")

            self.addTool(dbConnection, 15, 5, "CNC router")
            self.addTool(dbConnection, 16, 5, "Metal Lathe")
            self.addTool(dbConnection, 17, 5, "Table Saw")
            self.addTool(dbConnection, 18, 5, "Power Miter Saw")

            dbConnection.execute('''CREATE TABLE certifications
                                 (user_id       TEXT PRIMARY KEY,
                                  tool_id       INTEGER,
                                  certifier_id  TEXT,
                                  date          TIMESTAMP,
                                  level         INTEGER default 0)''')

    def addCertification(self, dbConnection, barcode, tool_id, level, date, certifier):
        # date needs to be changed to match format we want

        dbConnection.execute('''INSERT INTO certifications(user_id, tool_id, certifier_id, date, level)
                                SELECT ?, ?, ?, ?, ?
                                WHERE NOT EXISTS(SELECT 1 FROM certifications WHERE user_id=? AND tool_id=? AND level=?)''',
                             (barcode, tool_id, certifier, date, level, barcode, tool_id, level))

    def parseCert(self, str):
        str = str.upper()
        for level in ['BASIC', 'CERTIFIED', 'DOF', 'INSTRUCTOR', 'CERTIFIER']:
            if str.startswith(level):
                if str == level:
                    return (level, '')
                return (level, str[len(level) + 1:])
        return ('INVALID', '')

    def importFromCSV(self, filename, members, dbConnection):
        tool_dict = {4: 1, 5: 2, 6: 3, 7: 4, 9: 5, 10: 6, 11: 7, 13: 8, 14: 9,
                     15: 10, 17: 11, 18: 12, 19: 13, 20: 14, 22: 15, 23: 16, 24: 17, 25: 18}
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            cert_level = 0
            cert_date = ''
            for row in reader:
                barcode = members.getBarcode(row[2])
                if barcode:
                    for i in range(4, 26):
                        if row[i] and row[i] != 'N/A':
                            (level, date) = self.parseCert(row[i])
                            self.addCertification(
                                dbConnection, barcode, tool_dict[i], level, date, 'LEGACY')
                else:
                    print('Name not found: ', row[2])

        # unit test
if __name__ == "__main__":  # pragma no cover
    DB_STRING = 'data/test.db'
    certifications = Certifications(DB_STRING)
    certifications.createTable()
    certifications.importFromCSV("test.csv")
