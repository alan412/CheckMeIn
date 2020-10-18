import sqlite3
import os
import datetime
import re
from enum import IntEnum
from collections import namedtuple
from members import Members

TeamMember = namedtuple('TeamMember', ['name', 'barcode', 'type'])


class Status(IntEnum):
    inactive = 0
    active = 1


class TeamMemberType(IntEnum):
    student = 0
    mentor = 1
    coach = 2


class TeamInfo(object):
    def __init__(self, teamId, programName, programNumber, name, startDate):
        self.teamId = teamId
        self.programName = programName
        self.programNumber = programNumber
        self.name = name
        self.startDate = startDate

    def getProgramId(self):
        return f'{self.programName}{self.programNumber}' if self.programNumber else self.programName


class Teams(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version):  # pragma: no cover
        if db_schema_version < 5:
            dbConnection.execute('''CREATE TABLE teams
                                 (team_id INTEGER PRIMARY KEY,
                                 name TEXT UNIQUE,
                                  active INTEGER default 1)''')
            dbConnection.execute('''CREATE TABLE team_members
                                 (team_id TEXT, barcode TEXT, type INTEGER default 0)''')
        if db_schema_version < 10:
            dbConnection.execute('''CREATE TABLE new_teams 
                                 (team_id INTEGER PRIMARY_KEY,
                                        program_name TEXT,
                                        program_number INTEGER,
                                        team_name TEXT,
                                        start_date TIMESTAMP,
                                        active INTEGER default 1,
                                        CONSTRAINT unq UNIQUE (program_name, program_number, start_date))
            ''')
            now = datetime.datetime.now()
            for row in dbConnection.execute("SELECT * FROM teams"):
                dbConnection.execute('''
                    INSERT INTO new_teams VALUES (?,?,?,?,?,?)''',
                                     (row[0], 'LEGACY', row[0], row[1], now, '1'))
            dbConnection.execute('''DROP TABLE teams''')
            dbConnection.execute(
                '''ALTER TABLE new_teams RENAME TO teams''')

    def createTeam(self, dbConnection, program_name, program_number, team_name):
        now = datetime.datetime.now()
        try:
            dbConnection.execute(
                "INSERT INTO teams VALUES (NULL,?,?,?,?,1)", (program_name.upper(), program_number, team_name, now))
            return ""
        except sqlite3.IntegrityError:
            return "Team name already exists"

    def getActiveTeamList(self, dbConnection):
        dictTeams = {}
        for row in dbConnection.execute('''SELECT team_id, program_name, program_number, team_name, start_date
                                FROM teams
                                WHERE (active = ?)
                                ORDER BY program_name, program_number''', (Status.active,)):

            newTeam = TeamInfo(row[0], row[1], row[2], row[3], row[4])
            programId = newTeam.getProgramId()
            if programId in dictTeams:
                if dictTeams[programId].startDate < newTeam.startDate:
                    dictTeams[programId] = newTeam
            else:
                dictTeams[programId] = newTeam

        return dictTeams.values()

    def splitProgramInfo(self, programId):
        program_name = ''
        program_number = 0
        x = re.search(r"[1-9][0-9]*$", programId)
        if not x:
            program_name = programId
        else:
            program_number = int(x.group())
            (end, _) = x.span()
            program_name = x.string[:end]
        return (program_name, program_number)

    def getTeamFromProgramInfo(self, dbConnection, name, number):
        for row in dbConnection.execute('''SELECT team_id, program_name, program_number, team_name, start_date
                                FROM teams
                                WHERE (active = ? AND program_name = ? AND program_number = ?)
                                ORDER BY start_date DESC LIMIT 1''', (Status.active, name.upper(), number)):
            return TeamInfo(row[0], row[1], row[2], row[3], row[4])
        return None

    def teamNameFromId(self, dbConnection, team_id):
        data = dbConnection.execute(
            "SELECT * FROM teams WHERE (team_id=?)", (team_id, )).fetchone()
        if data:
            return data[3]
        return ''

    def addTeamMembers(self, dbConnection, team_id, listStudents, listMentors, listCoaches):
        fullList = []

        for student in listStudents:
            fullList.append((student, TeamMemberType.student))
        for mentor in listMentors:
            fullList.append((mentor, TeamMemberType.mentor))
        for coach in listCoaches:
            fullList.append((coach, TeamMemberType.coach))

        # Should it check to make sure team_id is valid?
            for member in fullList:
                dbConnection.execute("INSERT INTO team_members VALUES (?, ?, ?)",
                                     (team_id, member[0], member[1]))

    def getTeamMembers(self, dbConnection, team_id):
        listMembers = []
        for row in dbConnection.execute('''SELECT displayName,type,team_members.barcode
                            FROM team_members
                            INNER JOIN members ON members.barcode = team_members.barcode
                            WHERE (team_id == ?)
                            ORDER BY type, displayName''', (team_id,)):
            listMembers.append(TeamMember(row[0], row[2], row[1]))
        return listMembers
