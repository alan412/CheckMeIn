import datetime
import sqlite3
import cherrypy

from webBase import WebBase
from accounts import Role
from tracing import Tracing


class WebReports(WebBase):
    def checkPermissions(self, source="/reports"):
        super().checkPermissions(Role.ADMIN, source)

    @cherrypy.expose
    def index(self, error=""):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            firstDate = self.engine.reports.getEarliestDate(
                dbConnection).isoformat()
            todayDate = datetime.date.today().isoformat()
            reportList = self.engine.customReports.get_report_list(
                dbConnection)
            activeMembers = self.engine.members.getActive(dbConnection)
            guests = self.engine.guests.getGuests(dbConnection, numDays=30)
        return self.template('reports.mako',
                             firstDate=firstDate, todayDate=todayDate,
                             reportList=reportList, activeMembers=activeMembers, guests=guests, error=error)

    @cherrypy.expose
    def tracing(self, numDays, barcode=None):
        if not barcode:
            return self.index(error="No member selected")

        self.checkPermissions()

        with self.dbConnect() as dbConnection:
            dictVisits = Tracing().getDictVisits(dbConnection, barcode, numDays)
            (_, displayName) = self.engine.members.getName(
                dbConnection, barcode)
            if not displayName:
                (_, displayName) = self.engine.guests.getName(
                    dbConnection, barcode)

        return self.template('tracing.mako',
                             displayName=displayName,
                             dictVisits=dictVisits,
                             error="")

    @cherrypy.expose
    def standard(self, startDate, endDate):
        self.checkPermissions()
        return self.template('report.mako', stats=self.engine.reports.getStats(self.dbConnect(), startDate, endDate))

    @cherrypy.expose
    def graph(self, startDate, endDate):
        self.checkPermissions()
        cherrypy.response.headers['Content-Type'] = "image/png"
        stats = self.engine.reports.getStats(
            self.dbConnect(), startDate, endDate)
        return stats.getBuildingUsageGraph()

    @cherrypy.expose
    def saveCustom(self, sql, report_name):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            error = self.engine.customReports.saveCustomSQL(
                dbConnection, sql, report_name)
        return self.index(error)

    @cherrypy.expose
    def savedCustom(self, report_id, error=''):
        self.checkPermissions()
        title = "Error"
        sql = ""
        try:
            (title, sql, header, data) = self.engine.customReports.customReport(report_id)
        except sqlite3.OperationalError as e:
            data = repr(e)
            header = ["Error"]

        return self.template('customSQL.mako', report_title=title, sql=sql, data=data, header=header)

    @cherrypy.expose
    def customSQLReport(self, sql):
        self.checkPermissions()
        try:
            (header, data) = self.engine.customReports.customSQL(sql)
        except sqlite3.OperationalError as e:
            data = repr(e)
            header = ["Error"]

        return self.template('customSQL.mako', sql=sql, header=header, data=data)

    @cherrypy.expose
    def teamList(self):
        self.checkPermissions()
        with self.dbConnect() as dbConnection:
            teams = self.engine.teams.getActiveTeamList(dbConnection)
            for team in teams:
                team.members = self.engine.teams.getTeamMembers(
                    dbConnection, team.teamId)
        return self.template('teamReport.mako', teams=teams)
