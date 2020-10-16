import datetime
import cherrypy
from webBase import WebBase


class WebAdminStation(WebBase):
    # Admin
    @cherrypy.expose
    def index(self, error=""):
        with self.dbConnect() as dbConnection:
            forgotDates = []
            for date in self.engine.reports.getForgottenDates(dbConnection):
                forgotDates.append(date.isoformat())
            teamList = self.engine.teams.getActiveTeamList(dbConnection)
        return self.template('admin.mako', forgotDates=forgotDates,
                             teamList=teamList, error=error)

    @cherrypy.expose
    def emptyBuilding(self):
        with self.dbConnect() as dbConnection:
            self.engine.visits.emptyBuilding(dbConnection, "")
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def bulkAddMembers(self, csvfile):
        with self.dbConnect() as dbConnection:
            error = self.engine.members.bulkAdd(dbConnection, csvfile)
        return self.index(error)

    @cherrypy.expose
    def fixData(self, date):
        with self.dbConnect() as dbConnection:
            data = self.engine.reports.getData(dbConnection, date)
        return self.template('fixData.mako', date=date, data=data)

    @cherrypy.expose
    def oops(self):
        with self.dbConnect() as dbConnection:
            self.engine.visits.oopsForgot(dbConnection)
        return self.index('Oops is fixed. :-)')

    @cherrypy.expose
    def fixed(self, output):
        with self.dbConnect() as dbConnection:
            self.engine.visits.fix(dbConnection, output)
        return self.index()

    @cherrypy.expose
    def createTeam(self, team_name):
        # TODO: needs to be fixed
        error = self.engine.teams.createTeam(
            self.dbConnect(), "Sample", "", team_name)

        return self.index(error)

    @cherypy.expose
    def updateKeyholders(self, keyholders):
        keyholderList = keyholders.split(',')
        with self.dbConnect() as dbConnection:
            self.engine.keyholders.updateKeyholders(
                dbConnection, keyholderList)
        return self.index('Keyholders Updated')
