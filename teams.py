import sqlite3
import os
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

class Teams(object):
    def __init__(self):
        pass

    def migrate(self, dbConnection, db_schema_version): # pragma: no cover
        if db_schema_version < 5:
            dbConnection.execute('''CREATE TABLE teams
                                 (team_id INTEGER PRIMARY KEY,
                                 name TEXT UNIQUE,
                                  active INTEGER default 1)''')
            dbConnection.execute('''CREATE TABLE team_members
                                 (team_id TEXT, barcode TEXT, type INTEGER default 1)''')

    def createTeam(self, dbConnection, name):
        try:
            dbConnection.execute(
                "INSERT INTO teams VALUES (NULL,?,1)", (name, ))
            return ""
        except sqlite3.IntegrityError:
            return "Team name already exists"

    def getTeamList(self, dbConnection):
        team_list = []
        for row in dbConnection.execute('''SELECT team_id, name
                                FROM teams
                                WHERE (active = ?)
                                ORDER BY name''', (Status.active,)):
            team_list.append((row[0], row[1]))
        return team_list

    def teamIdFromName(self, dbConnection, name):
        data = dbConnection.execute(
            "SELECT * FROM teams WHERE (name=?)", (name, )).fetchone()
        if data:
            return data[0]
        return ''

    def teamNameFromId(self, dbConnection, team_id):
        data = dbConnection.execute(
            "SELECT * FROM teams WHERE (team_id=?)", (team_id, )).fetchone()
        if data:
            return data[1]
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