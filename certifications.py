import datetime
import sqlite3
import os
import csv
import members
import utils

from enum import IntEnum


class CertificationLevels(IntEnum):
    NONE = 0
    BASIC = 1
    CERTIFIED = 10
    DOF = 20
    INSTRUCTOR = 30
    CERTIFIER = 40


class ToolUser(object):
    def __init__(self, displayName, barcode):
        self.tools = {}
        self.displayName = displayName
        self.barcode = barcode

    def addTool(self, tool_id, date, level):
        if not date:
            date = datetime.datetime(2019, 1, 1)
        if tool_id in self.tools:
            (currDate, nil) = self.tools[tool_id]
            if date > currDate:
                self.tools[tool_id] = (date, level)
        else:
            self.tools[tool_id] = (date, level)

    def getTool(self, tool_id):
        try:
            return self.tools[tool_id]
        except KeyError:
            return ("", CertificationLevels.NONE)

    def getHTMLCellTool(self, tool_id):
        (dateObj, level) = self.getTool(tool_id)
        date = str(dateObj)[:7]

        HTMLDetails = {
            CertificationLevels.NONE:
            '<TD class="clNone"></TD>',
            CertificationLevels.BASIC:
            f'<TD class="clBasic">BASIC<br/>{date}</TD>',
            CertificationLevels.CERTIFIED:
            f'<TD class="clCertified">CERTIFIED<br/>{date}</TD>',
            CertificationLevels.DOF:
            f'<TD class="clDOF">DOF<br/>{date}</TD>',
            CertificationLevels.INSTRUCTOR:
            f'<TD class="clInstructor">Instructor<br/>{date}</TD>',
            CertificationLevels.CERTIFIER:
            f'<TD class="clCertifier">Certifier<br/>{date}</TD>'
        }
        try:
            return HTMLDetails[level]
        except KeyError:  # pragma: no cover
            return "Key: " + str(level)


class Certifications(object):
    def __init__(self):
        self.levels = {
            CertificationLevels.NONE: 'NONE',
            CertificationLevels.BASIC: 'BASIC',
            CertificationLevels.CERTIFIED: 'CERTIFIED',
            CertificationLevels.DOF: 'DOF',
            CertificationLevels.INSTRUCTOR: 'INSTRUCTOR',
            CertificationLevels.CERTIFIER: 'CERTIFIER'
        }

    def addTool(self,
                dbConnection,
                tool_id,
                grouping,
                name,
                restriction=0,
                comments=''):  # pragma: no cover
        dbConnection.execute('INSERT INTO tools VALUES(?,?,?,?,?)',
                             (tool_id, grouping, name, restriction, comments))

    def addTools(self, dbConnection):  # pragma: no cover
        tools = [[1, 1, "Sheet Metal Brake"], [2, 1, "Blind Rivet Gun"],
                 [3, 1, "Stretcher Shrinker"], [4, 1, "3D printers"],
                 [5, 2, "Power Hand Drill"], [6, 2, "Solder Iron"],
                 [7, 2, "Dremel"], [8, 3, "Horizontal Band Saw"],
                 [9, 3, "Drill Press"], [10, 3, "Grinder / Sander"],
                 [11, 4, "Scroll Saw"], [12, 4, "Table Mounted Jig Saw"],
                 [13, 4, "Vertical Band Saw"], [14, 4, "Jig Saw"],
                 [15, 5, "CNC router"], [16, 5, "Metal Lathe"],
                 [17, 5, "Table Saw"], [18, 5, "Power Miter Saw"]]
        for tool in tools:
            if tool[2] == "Power Miter Saw" or tool[
                    2] == "Table Saw":  # Over 18 only tools
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
        if db_schema_version < 16:
            self.addTool(dbConnection, 19, 3, "Grinder")
            dbConnection.execute(
                "UPDATE tools SET name='Sander' WHERE id=10")
            for row in dbConnection.execute(
                '''SELECT user_id, tool_id, date, level, certifier_id FROM certifications
                                        WHERE tool_id=10'''):
                self.addCertification(dbConnection, row[0], 19, row[3], row[2],
                                      row[4])

    def injectData(self, dbConnection, data):
        for datum in data:
            self.addCertification(dbConnection, datum["barcode"],
                                  datum["tool_id"], datum["level"],
                                  datum["date"], datum["certifier"])

    def addNewCertification(self, dbConnection, member_id, tool_id, level,
                            certifier):
        return self.addCertification(dbConnection, member_id, tool_id, level,
                                     datetime.datetime.now(), certifier)

    def addCertification(self, dbConnection, barcode, tool_id, level, date,
                         certifier):
        # TODO: need to verify that the certifier can indeed certify on this tool

        dbConnection.execute(
            '''INSERT INTO certifications(user_id, tool_id, certifier_id, date, level)
                                SELECT ?, ?, ?, ?, ?''',
            (barcode, tool_id, certifier, date, level))

    def getAllUserList(self, dbConnection):
        users = {}
        for row in dbConnection.execute(
            '''SELECT user_id, tool_id, date, level, v_current_members.displayName FROM certifications
                                            INNER JOIN v_current_members ON v_current_members.barcode=user_id
                                            ORDER BY v_current_members.displayName'''):
            try:
                users[row[0]].addTool(row[1], row[2], row[3])
            except KeyError:
                users[row[0]] = ToolUser(row[4], row[0])
                users[row[0]].addTool(row[1], row[2], row[3])
        return users

    def getInBuildingUserList(self, dbConnection):
        users = {}
        for row in dbConnection.execute(
                '''SELECT user_id, tool_id, date, level, members.displayName FROM certifications
                                        INNER JOIN members ON members.barcode=user_id
                                        INNER JOIN visits ON visits.barcode=user_id
                                        WHERE visits.status="In"
                                        ORDER BY members.displayName'''):
            try:
                users[row[0]].addTool(row[1], row[2], row[3])
            except KeyError:
                users[row[0]] = ToolUser(row[4], row[0])
                users[row[0]].addTool(row[1], row[2], row[3])
        return users

    def getTeamUserList(self, dbConnection, team_id):
        users = {}
        # This is because SQLITE doesn't support RIGHT JOIN
        for row in dbConnection.execute(
            '''
                SELECT team_members.barcode, displayName, type FROM
                team_members
                INNER JOIN members ON members.barcode=team_members.barcode
                WHERE (team_id == ?)
                ORDER BY type DESC, displayName ASC
            ''', (team_id,)):
            users[row[0]] = ToolUser(row[1], row[0])

        for row in dbConnection.execute(
            '''SELECT user_id, tool_id, date, level, members.displayName FROM certifications
                                            INNER JOIN members ON members.barcode=user_id
                                            INNER JOIN team_members ON members.barcode=team_members.barcode
                                            WHERE team_members.team_id = ?
                                            ORDER BY team_members.type DESC, members.displayName ASC''',
                (team_id, )):
            try:
                users[row[0]].addTool(row[1], row[2], row[3])
            except KeyError:
                users[row[0]] = ToolUser(row[4], row[0])
                users[row[0]].addTool(row[1], row[2], row[3])
        # This is because SQLITE doesn't support RIGHT JOIN

        return users

    def getUserList(self, dbConnection, user_id):
        users = {}
        for row in dbConnection.execute(
            '''SELECT user_id, tool_id, date, level, members.displayName FROM certifications
                                            INNER JOIN members ON members.barcode=user_id
                                            WHERE user_id = ?''',
                (user_id, )):
            try:
                users[row[0]].addTool(row[1], row[2], row[3])
            except KeyError:
                users[row[0]] = ToolUser(row[4], row[0])
                users[row[0]].addTool(row[1], row[2], row[3])
        return users

    def getAllTools(self, dbConnection):
        tools = []
        for row in dbConnection.execute(
                'SELECT id, name, grouping FROM tools ORDER BY grouping, id ASC', ()):
            tools.append([row[0], row[1], row[2]])
        return tools

    def getToolsFromList(self, dbConnection, inputStr):
        tools = self.getAllTools(dbConnection)
        inputTools = inputStr.split("_")
        newToolList = []

        for tool in tools:
            if str(tool[0]) in inputTools:
                newToolList.append(tool)
        return newToolList

    def getListCertifyTools(self, dbConnection, user_id):
        tools = []
        for row in dbConnection.execute(
            '''SELECT id, name FROM tools
                     INNER JOIN certifications ON certifications.tool_id = id
                     WHERE user_id = ? AND level >= ? ORDER BY name ASC''',
                (user_id, CertificationLevels.CERTIFIER)):
            tools.append([row[0], row[1]])
        return tools

    def getToolName(self, dbConnection, tool_id):
        data = dbConnection.execute('SELECT name FROM tools WHERE id == ?',
                                    (tool_id, )).fetchone()
        return data[0]

    def getLevelName(self, level):
        return self.levels[CertificationLevels(int(level))]

    def emailCertifiers(self, name, toolName, levelDescription, certifierName):
        emailAddress = "shopcertifiers@theforgeinitiative.org"
        msg = f"{name} was just certified as {levelDescription} on {toolName} by {certifierName}!!"

        utils.sendEmail("Shop Certifiers", emailAddress,
                        "New Certification", msg)
        return ''
