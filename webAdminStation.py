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
        error = self.engine.members.bulkAdd(self.dbConnect(), csvfile)
        return self.index(error)

    @cherrypy.expose
    def fixData(self, date):
        data = self.engine.reports.getData(self.dbConnect(), date)
        return self.template('fixData.mako', date=date, data=data)

    @cherrypy.expose
    def oops(self):
        self.engine.visits.oopsForgot(self.dbConnect())
        return self.index('Oops is fixed. :-)')

    @cherrypy.expose
    def fixed(self, output):
        self.engine.visits.fix(self.dbConnect(), output)
        return self.index()

    @cherrypy.expose
    def createTeam(self, team_name):
        # TODO: needs to be fixed
        error = self.engine.teams.createTeam(
            self.dbConnect(), "Sample", "", team_name)

        return self.index(error)
