import datetime
import sqlite3
import cherrypy

from webBase import WebBase

class WebReports(WebBase):
    @cherrypy.expose
    def index(self, error=""):
        with self.dbConnect() as dbConnection:
            firstDate = self.engine.reports.getEarliestDate(
                dbConnection).isoformat()
            todayDate = datetime.date.today().isoformat()
            reportList = self.engine.customReports.get_report_list(
                dbConnection)
        return self.template('reports.mako', 
                             firstDate=firstDate, todayDate=todayDate,
                             reportList=reportList, error=error)
    @cherrypy.expose
    def standard(self, startDate, endDate):
        return self.template('report.mako', stats=self.engine.reports.getStats(self.dbConnect(), startDate, endDate))
    
    @cherrypy.expose
    def graph(self, startDate, endDate):
        cherrypy.response.headers['Content-Type'] = "image/png"
        stats = self.engine.reports.getStats(
            self.dbConnect(), startDate, endDate)
        return stats.getBuildingUsageGraph()

    @cherrypy.expose
    def saveCustom(self, sql, report_name):
        error = self.engine.customReports.saveCustomSQL(
            self.dbConnect(), sql, report_name)
        return self.index(error)

    @cherrypy.expose
    def savedCustom(self, report_id, error=''):
        title = "Error"
        sql = ""
        try:
            (title, sql, data) = self.engine.customReports.customReport(report_id)
        except sqlite3.OperationalError as e:
            data = repr(e)

        return self.template('customSQL.mako', report_title=title, sql=sql, data=data)

    @cherrypy.expose
    def customSQLReport(self, sql):
        try:
            data = self.engine.customReports.customSQL(sql)
        except sqlite3.OperationalError as e:
            data = repr(e)

        return self.template('customSQL.mako', sql=sql, data=data)
