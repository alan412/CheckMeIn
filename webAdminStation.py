import datetime
import cherrypy
from webBase import WebBase

class WebAdminStation(WebBase):
### Admin
    @cherrypy.expose
    def index(self, error=""):
        with self.dbConnect() as dbConnection:
            firstDate = self.engine.reports.getEarliestDate(
                dbConnection).isoformat()
            todayDate = datetime.date.today().isoformat()
            forgotDates = []
            for date in self.engine.reports.getForgottenDates(dbConnection):
                forgotDates.append(date.isoformat())
            teamList = self.engine.teams.getTeamList(dbConnection)
            reportList = self.engine.customReports.get_report_list(
                dbConnection)
        return self.template('admin.mako', forgotDates=forgotDates,
                             firstDate=firstDate, todayDate=todayDate,
                             teamList=teamList, reportList=reportList, error=error)
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
        error = self.engine.teams.createTeam(
            self.dbConnect(), team_name)
        return self.index(error)