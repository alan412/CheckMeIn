import datetime
import cherrypy
from passwords import Passwords, Role
from webBase import WebBase


class Cookie(object):
    def __init__(self, name):
        self.name = name

    def get(self, default=''):
        result = default
        try:
            result = cherrypy.session.get(self.name)
            if not result:
                self.set(default)
                result = default
        except:
            self.set(default)
        return result

    def set(self, value):
        cherrypy.session[self.name] = value
        return value

    def delete(self):
        cherrypy.session.pop(self.name, None)


class WebAdminStation(WebBase):
    @cherrypy.expose
    def logout(self):
        Cookie('username').delete()
        raise cherrypy.HTTPRedirect("/admin/login")

    @cherrypy.expose
    def login(self, error=""):
        return self.template('login.mako', error=error)

    @cherrypy.expose
    def loginAttempt(self, username, password):
        with self.dbConnect() as dbConnection:
            # For seeding database only - DO NOT KEEP!!!
            # self.engine.passwords.addUser(
            #    dbConnection, username, password, '123456', Role.admin)
            barcode = self.engine.passwords.getBarcode(
                dbConnection, username, password, Role.admin)
            if not barcode:
                return self.template('login.mako', error="Invalid username/password")
            Cookie('barcode').set(barcode)
            Cookie('username').set(username)
        raise cherrypy.HTTPRedirect("/admin")

    # Admin
    @cherrypy.expose
    def index(self, error=""):
        if not Cookie('barcode').get(''):
            raise cherrypy.HTTPRedirect("/admin/login")
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
        if not Cookie('barcode').get(''):
            raise cherrypy.HTTPRedirect("/admin/login")
        with self.dbConnect() as dbConnection:
            error = self.engine.members.bulkAdd(dbConnection, csvfile)
        return self.index(error)

    @cherrypy.expose
    def fixData(self, date):
        if not Cookie('barcode').get(''):
            raise cherrypy.HTTPRedirect("/admin/login")
        with self.dbConnect() as dbConnection:
            data = self.engine.reports.getData(dbConnection, date)
        return self.template('fixData.mako', date=date, data=data)

    @cherrypy.expose
    def oops(self):
        if not Cookie('barcode').get(''):
            raise cherrypy.HTTPRedirect("/admin/login")
        with self.dbConnect() as dbConnection:
            self.engine.visits.oopsForgot(dbConnection)
        return self.index('Oops is fixed. :-)')

    @cherrypy.expose
    def fixed(self, output):
        if not Cookie('barcode').get(''):
            raise cherrypy.HTTPRedirect("/admin/login")
        with self.dbConnect() as dbConnection:
            self.engine.visits.fix(dbConnection, output)
        return self.index()

    @cherrypy.expose
    def createTeam(self, team_name):
        if not Cookie('barcode').get(''):
            raise cherrypy.HTTPRedirect("/admin/login")
        # TODO: needs to be fixed
        error = self.engine.teams.createTeam(
            self.dbConnect(), "Sample", "", team_name)

        return self.index(error)

    @cherrypy.expose
    def updateKeyholders(self, keyholders):
        # TODO: this will go away when doorapp gets keyholders from checkmein
        keyholderList = keyholders.split(',')
        with self.dbConnect() as dbConnection:
            self.engine.keyholders.updateKeyholders(
                dbConnection, keyholderList)
        return self.index('Keyholders Updated')
