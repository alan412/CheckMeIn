import datetime
import sqlite3
import os
import csv
import members
from enum import IntEnum


class CertificationLevels(IntEnum):
    NONE = 0
    BASIC = 1
    CERTIFIED = 10
    DOF = 20
    INSTRUCTOR = 30
    CERTIFIER = 40


class ToolUser(object):
    def __init__(self):
        self.tools = {}

    def addTool(self, tool_id, date, level):
        if tool_id in self.tools:
            (nil, currLevel) = self.tools[tool_id]
            if level > currLevel:
                self.tools[tool_id] = (date, level)
        else:
            self.tools[tool_id] = (date, level)

    def getTool(self, tool_id):
        try:
            return self.tools[tool_id]
        except KeyError:
            return ("", CertificationLevels.NONE)

    def getHTMLCellTool(self, tool_id):
        (date, level) = self.getTool(tool_id)
        HTMLDetails = {
            CertificationLevels.NONE:  '<TD class="clNone"></TD>',
            CertificationLevels.BASIC: '<TD class="clBasic">BASIC</TD>',
            CertificationLevels.CERTIFIED: '<TD class="clCertified">CERTIFIED</TD>',
            CertificationLevels.DOF: '<TD class="clDOF">DOF</TD>',
            CertificationLevels.INSTRUCTOR: '<TD class="clInstructor">Instructor</TD>',
            CertificationLevels.CERTIFIER: '<TD class="clCertifier">Certifier</TD>'
        }
        try:
            return HTMLDetails[level]
        except KeyError:
            return "Key: " + str(level)


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
        tools = [[1, 1, "Sheet Metal Brake"],
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
                 [18, 5, "Power Miter Saw"]]
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
                                 (user_id       TEXT,
                                  tool_id       INTEGER,
                                  certifier_id  TEXT,
                                  date          TIMESTAMP,
                                  level         INTEGER default 0)''')
            self.addTools(dbConnection)

    def addNewCertification(self, member_id, tool_id, level, certifier):
        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            return self.addCertification(c, member_id, tool_id, level, datetime.datetime.now(), certifier)

    def addCertification(self, dbConnection, barcode, tool_id, level, date, certifier):
        # date needs to be changed to match format we want

        dbConnection.execute('''INSERT INTO certifications(user_id, tool_id, certifier_id, date, level)
                                SELECT ?, ?, ?, ?, ?
                                WHERE NOT EXISTS(SELECT 1 FROM certifications WHERE user_id=? AND tool_id=? AND level=?)''',
                             (barcode, tool_id, certifier, date, level, barcode, tool_id, level))

    def getToolList(self, certifier_id):
        return self.getListCertifyTools(sqlite3.connect(self.database), certifier_id)

    def getUserList(self):
        users = {}
        dbConnection = sqlite3.connect(self.database)
        for row in dbConnection.execute('''SELECT user_id, tool_id, date, level FROM certifications
                                        INNER JOIN members ON members.barcode=user_id
                                        ORDER BY members.displayName'''):
            try:
                users[row[0]].addTool(row[1], row[2], row[3])
            except KeyError:
                users[row[0]] = ToolUser()
                users[row[0]].addTool(row[1], row[2], row[3])
        return users

    def getAllTools(self):
        tools = []
        dbConnection = sqlite3.connect(self.database)
        for row in dbConnection.execute('SELECT id, name, grouping FROM tools', ()):
            tools.append([row[0], row[1], row[2]])
        return tools

    def getToolsFromList(self, inputStr):
        tools = self.getAllTools()
        inputTools = inputStr.split("_")
        newToolList = []
        print(inputTools)

        for tool in tools:
            if str(tool[0]) in inputTools:
                newToolList.append(tool)
            else:
                print("Not Found:", tool)
        return newToolList

    def getListCertifyTools(self, dbConnection, user_id):
        tools = []
        for row in dbConnection.execute('''SELECT id, name FROM tools
                 INNER JOIN certifications ON certifications.tool_id = id
                 WHERE user_id = ? AND level >= ?''', (user_id, CertificationLevels.CERTIFIER)):
            tools.append([row[0], row[1]])
        return tools

    def parseCert(self, str):
        levels = {
            CertificationLevels.BASIC: 'BASIC',
            CertificationLevels.CERTIFIED: 'CERTIFIED',
            CertificationLevels.DOF: 'DOF',
            CertificationLevels.INSTRUCTOR: 'INSTRUCTOR',
            CertificationLevels.CERTIFIER: 'CERTIFIER'
        }
        str = str.upper()
        for level, name in levels.items():
            if str.startswith(name):
                if str == name:
                    return (level, '')
                return (level, str[len(name) + 1:])
        return (CertificationLevels.NONE, '')

    def importFromCSV(self, filename, members, dbConnection):
        tool_dict = {4: 1, 5: 2, 6: 3, 7: 4, 9: 5, 10: 6, 11: 7, 13: 8, 14: 9,
                     15: 10, 17: 11, 18: 12, 19: 13, 20: 14, 22: 15, 23: 16, 24: 17, 25: 18}
        print('--- IMPORT FROM ' + filename + ' ---')
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            cert_level = 0
            cert_date = ''
            for row in reader:
                barcode = members.getBarcode(row[2], dbConnection)
                if not barcode and row[2]:
                    names = row[2].split(' ')
                    try:
                        displayName = ''
                        for i in range(0, len(names) - 1):
                            displayName += names[i] + ' '
                        displayName += names[len(names) - 1][0]
                        barcode = members.getBarcode(displayName, dbConnection)
                    except:
                        print("Exception: ", names)
                if barcode:
                    for i in range(4, 26):
                        if row[i] and row[i] != 'N/A':
                            (level, date) = self.parseCert(row[i])
                            if level != CertificationLevels.NONE:
                                self.addCertification(
                                    dbConnection, barcode, tool_dict[i], level, date, 'LEGACY')
                elif row[2]:
                    print('Name not found: ', row[2])


        # unit test
if __name__ == "__main__":  # pragma no cover
    DB_STRING = 'data/test.db'
    certifications = Certifications(DB_STRING)
    certifications.createTable()
    certifications.importFromCSV("test.csv")
