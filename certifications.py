import sqlite3
import os
import csv
from enum import IntEnum


class CertificationLevels(IntEnum):
    NONE = 0
    BASIC = 1
    CERTIFIED = 10
    DOF = 20
    INSTRUCTOR = 30
    CERTIFIER = 40


class Certifications(object):
    def __init__(self, database):
        self.database = database

    def createTable(self):
        with sqlite3.connect(self.database) as c:
            self.migrate(c, 0)

    def addTool(self, dbConnection, tool_id, grouping, name, restriction=0, comments=''):
        dbConnection.execute('INSERT INTO tools VALUES(?,?,?,?,?)',
                             (tool_id, grouping, name, restriction, comments))

    def addTools(self, dbConnection):
        tools = {[1, 1, "Sheet Metal Brake"],
                 [2, 1, "Blind Rivet Gun"],
                 [3, 1, "Stretcher Shrinker"],
                 [4, 1, "3D printers"],

                 [5, 2, "Power Hand Drill"],
                 [6, 2, "Solder Iron"],
                 [7, 2, "Dremel"],

                 [8, 3, "Horizontal Band Saw"],
                 [9, 3, "Drill Press"],
                 [10, 3, "Grinder / Sander"],

                 [11, 4, "Scroll Saw"],
                 [12, 4, "Table Mounted Jig Saw"],
                 [13, 4, "Vertical Band Saw"],
                 [14, 4, "Jig Saw"],

                 [15, 5, "CNC router"],
                 [16, 5, "Metal Lathe"],
                 [17, 5, "Table Saw"],
                 [18, 5, "Power Miter Saw"]}
        for tool in tools:
            if tool[2] == "Power Miter Saw" or tool[2] == "Table Saw":  # Over 18 only tools
                self.addTool(dbConnection, tool[0], tool[1], tool[2], 1)
            else:
                self.addTool(dbConnection, tool[0], tool[1], tool[2])

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

            dbConnection.execute('''CREATE TABLE certifications
                                 (user_id       TEXT PRIMARY KEY,
                                  tool_id       INTEGER,
                                  certifier_id  TEXT,
                                  change        TIMESTAMP,
                                  level         INTEGER default 0)''')

            self.addTools(dbConnection)

    def getListCertifyTools(self, dbConnection, user_id):
        tools = []
        for row in dbConnection.execute('''SELECT id, name FROM tools 
                 INNER JOIN certifications ON certifications.tool_id = id
                 WHERE user_id = ? AND level >= ?''', (user_id, CertificationLevels.CERTIFIER)):
            tools.append([row[0], row[1]])
        return tools

    def parseCert(self, str):
        str = str.upper()
        for level in ['BASIC', 'CERTIFIED', 'DOF', 'INSTRUCTOR', 'CERTIFIER']:
            if str.startswith(level):
                if str == level:
                    return (level, '')
                return (level, str[len(level) + 1:])
        return ('INVALID', '')

    def importFromCSV(self, filename):
        tool_dict = {4: 1, 5: 2, 6: 3, 7: 4, 9: 5, 10: 6, 11: 7, 13: 8, 14: 9,
                     15: 10, 17: 11, 18: 12, 19: 13, 20: 14, 22: 15, 23: 16, 24: 17, 25: 18}
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            cert_level = 0
            cert_date = ''
            for row in reader:
                print('Name: ', row[2])
                # TODO: See if name is legit, otherwise complain loudly
                for i in range(4, 26):
                    if row[i] and row[i] != 'N/A':
                        print(tool_dict[i], self.parseCert(row[i]))

        # unit test
if __name__ == "__main__":  # pragma no cover
    DB_STRING = 'data/test.db'
    try:
        os.remove(DB_STRING)   # Start with a new one
    except:
        pass  # Don't care if it didn't exist
    certifications = Certifications(DB_STRING)
    certifications.createTable()
    certifications.importFromCSV("test.csv")
