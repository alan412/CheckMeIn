import datetime
import cherrypy
import random
import sqlite3
import json
from accounts import Accounts, Role
from webBase import WebBase, Cookie
from cryptography.fernet import Fernet


class WebAdminStation(WebBase):
    def checkPermissions(self, source="/admin"):
        super().checkPermissions(Role.ADMIN, source)
    # Admin

    @cherrypy.expose
    def index(self, error=""):
        self.checkPermissions()

        with self.dbConnect() as dbConnection:
            forgotDates = []
            for date in self.engine.reports.getForgottenDates(dbConnection):
                forgotDates.append(date.isoformat())
            teamList = self.engine.teams.getActiveTeamList(dbConnection)
        return self.template('admin.mako', forgotDates=forgotDates,
                             teamList=teamList, error=error, username=Cookie('username').get(''))

    @cherrypy.expose
    def emptyBuilding(self):
        with self.dbConnect() as dbConnection:
            self.engine.visits.emptyBuilding(dbConnection, "")
            self.engine.accounts.removeKeyholder(dbConnection)
        return "Building Empty"

    @cherrypy.expose
    def bulkAddMembers(self, csvfile):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            error = self.engine.members.bulkAdd(dbConnection, csvfile)
        return self.index(error)

    @cherrypy.expose
    def fixData(self, date):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            data = self.engine.reports.getData(dbConnection, date)
        return self.template('fixData.mako', date=date, data=data)

    @cherrypy.expose
    def oops(self):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            self.engine.visits.oopsForgot(dbConnection)
        return self.index('Oops is fixed. :-)')

    @cherrypy.expose
    def fixed(self, output):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            self.engine.visits.fix(dbConnection, output)
        return self.index()

    @cherrypy.expose
    def teams(self, error=""):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            activeTeams = self.engine.teams.getActiveTeamList(dbConnection)
            activeMembers = self.engine.members.getActive(dbConnection)
            print("BEFORE ********************")
            coaches = self.engine.teams.getCoachesList(
                dbConnection, activeTeams)
            print("AFTER ********************")

        return self.template('adminTeams.mako', error=error, username=Cookie('username').get(''), activeTeams=activeTeams, activeMembers=activeMembers, coaches=coaches)

    @cherrypy.expose
    def addTeam(self, programName, programNumber, teamName, coach1, coach2):
        self.checkPermissions()
        with self.dbConnect() as connection:
            error = self.engine.teams.createTeam(
                connection, programName, programNumber, teamName)

        if not error:
            with self.dbConnect() as connection:
                teamInfo = self.engine.teams.getTeamFromProgramInfo(
                    connection, programName, programNumber)
                print(teamInfo, coach1, coach2)
                self.engine.teams.addTeamMembers(connection, teamInfo.teamId,
                                                 [], [], [coach1, coach2])
        return self.teams(error)

    @cherrypy.expose
    def createTeam(self, team_name):
        self.checkPermissions()
        # TODO: needs to be fixed
        error = self.engine.teams.createTeam(
            self.dbConnect(), "Sample", "", team_name)

        return self.index(error)

    @cherrypy.expose
    def users(self, error=""):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            users = self.engine.accounts.getUsers(dbConnection)
            nonUsers = self.engine.accounts.getNonAccounts(dbConnection)
        return self.template('users.mako', error=error, username=Cookie('username').get(''), users=users, nonAccounts=nonUsers)

    @cherrypy.expose
    def addUser(self, user, barcode, keyholder=0, admin=0, certifier=0, coach=0):
        error = ""
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
            tempPassword = ''.join(random.SystemRandom().choice(chars)
                                   for _ in range(12))
            role = Role()
            role.setAdmin(admin)
            role.setKeyholder(keyholder)
            role.setShopCertifier(certifier)
            role.setCoach(coach)
            try:
                self.engine.accounts.addUser(
                    dbConnection, user, tempPassword, barcode, role)
                # self.engine.accounts.forgotPassword(dbConnection, user)
            except sqlite3.IntegrityError:
                error = "Username already in use"
        return self.users(error)

    @cherrypy.expose
    def deleteUser(self, barcode):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            self.engine.accounts.removeUser(dbConnection, barcode)
        raise cherrypy.HTTPRedirect("/admin/users")

    @cherrypy.expose
    def changeAccess(self, barcode, admin=False, keyholder=False, certifier=False, coach=False):
        self.checkPermissions()
        newRole = Role()
        newRole.setAdmin(admin)
        newRole.setKeyholder(keyholder)
        newRole.setShopCertifier(certifier)
        newRole.setCoach(coach)

        with self.dbConnect() as dbConnection:
            self.engine.accounts.changeRole(dbConnection, barcode, newRole)
        raise cherrypy.HTTPRedirect("/admin/users")

    @cherrypy.expose
    def getKeyholderJSON(self):
        jsonData = ''
        with self.dbConnect() as dbConnection:
            keyholders = self.engine.accounts.getKeyholders(dbConnection)
            for keyholder in keyholders:
                keyholder['devices'] = []
                devices = self.engine.devices.getList(
                    dbConnection, keyholder['barcode'])
                for device in devices:
                    keyholder['devices'].append(
                        {'name': device.name, 'mac': device.mac})
        #    print(keyholders)
            jsonData = json.dumps(keyholders)
        # encrypt now
            with open('data/checkmein.key', 'rb') as key_file:
                key = key_file.read()
            f = Fernet(key)
            return f.encrypt(jsonData.encode('utf-8'))
