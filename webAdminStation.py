import datetime
import cherrypy
from accounts import Accounts, Role
from webBase import WebBase, Cookie


class WebAdminStation(WebBase):
    def checkPermissions(self):
        role = Role(Cookie('role').get(0))
        if not role.isAdmin():
            raise cherrypy.HTTPRedirect("/profile/login")
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
        raise cherrypy.HTTPRedirect("/")

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
    def createTeam(self, team_name):
        self.checkPermissions()
        # TODO: needs to be fixed
        error = self.engine.teams.createTeam(
            self.dbConnect(), "Sample", "", team_name)

        return self.index(error)

    @cherrypy.expose
    def users(self):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            users = self.engine.accounts.getUsers(dbConnection)
        return self.template('users.mako', error="", username=Cookie('username').get(''), users=users)

    @cherrypy.expose
    def deleteUser(self, barcode):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            self.engine.accounts.removeUser(dbConnection, barcode)
        raise cherrypy.HTTPRedirect("/admin/users")

    @cherrypy.expose
    def changeAccess(self, barcode, admin=False, keyholder=False):
        self.checkPermissions()
        newRole = Role()
        newRole.setAdmin(admin)
        newRole.setKeyholder(keyholder)

        with self.dbConnect() as dbConnection:
            self.engine.accounts.changeRole(dbConnection, barcode, newRole)
        raise cherrypy.HTTPRedirect("/admin/users")

    @cherrypy.expose
    def updateKeyholders(self, keyholders):
        # TODO: this will go away when doorapp gets keyholders from checkmein
        keyholderList = keyholders.split(',')
        with self.dbConnect() as dbConnection:
            self.engine.keyholders.updateKeyholders(
                dbConnection, keyholderList)
        return self.index('Keyholders Updated')
