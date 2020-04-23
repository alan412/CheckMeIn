import argparse
import datetime
import sqlite3
from mako.lookup import TemplateLookup
import cherrypy
import cherrypy.process.plugins
from visits import Visits
from teams import TeamMemberType

DB_STRING = 'data/checkMeIn.db'
KEYHOLDER_BARCODE = '999901'


class CheckMeIn(object):
    def __init__(self):
        self.lookup = TemplateLookup(
            directories=['HTMLTemplates'], default_filters=['h'])
        self.visits = Visits(DB_STRING)

    def dbConnect(self):
        return sqlite3.connect(DB_STRING, detect_types=sqlite3.PARSE_DECLTYPES)

    def template(self, name, **kwargs):
        return self.lookup.get_template(name).render(**kwargs)

    def showGuestPage(self, message=''):
        with self.dbConnect() as dbConnection:
            all_guests = self.visits.guests.getList(dbConnection)
            building_guests = self.visits.reports.guestsInBuilding(
                dbConnection)

        guests_not_here = [
            guest for guest in all_guests if guest not in building_guests]

        return self.template('guests.mako', message=message,
                             inBuilding=building_guests,
                             guestList=guests_not_here)

    def showCertifications(self, message, barcodes, tools, show_table_header=True):
        return self.template('certifications.mako', message=message,
                             show_table_header=show_table_header,
                             barcodes=barcodes,
                             tools=tools,
                             members=self.visits.members,
                             certifications=self.visits.certifications.getUserList())

    @cherrypy.expose
    def station(self, error=''):
        with self.dbConnect() as dbConnection:
            self.visits.checkBuilding(dbConnection)
            return self.template('station.mako',
                                 todaysTransactions=self.visits.reports.transactionsToday(
                                     dbConnection),
                                 numberPresent=self.visits.reports.numberPresent(
                                     dbConnection),
                                 uniqueVisitorsToday=self.visits.reports.uniqueVisitorsToday(
                                     dbConnection),
                                 keyholder_name=self.visits.getKeyholderName(
                                     dbConnection),
                                 error=error)

    @cherrypy.expose
    def who_is_here(self):
        return self.template('who_is_here.mako', now=datetime.datetime.now(),
                             whoIsHere=self.visits.reports.whoIsHere(self.dbConnect()
                                                                     ))

    @cherrypy.expose
    def keyholder(self, barcode):
        error = ''
        barcode = barcode.strip()
        with self.dbConnect() as dbConnection:
            if barcode == KEYHOLDER_BARCODE or (
                    barcode == self.visits.getActiveKeyholder(dbConnection)):
                self.visits.emptyBuilding(dbConnection)
            else:
                error = self.visits.setActiveKeyholder(dbConnection, barcode)
                if error:  # pragma: no cover # TODO after this case is added, remove no cover
                    return self.template('keyholder.mako', error=error)
        return self.station()

    @cherrypy.expose
    # later change this to be more ajaxy, but for now...
    def scanned(self, barcode):
        error = ''
# strip whitespace before or after barcode digits (occasionally a space comes before or after
        barcodes = barcode.split()
        with self.dbConnect() as dbConnection:
            for bc in barcodes:
                if (bc == KEYHOLDER_BARCODE) or (
                        bc == self.visits.getActiveKeyholder(dbConnection)):
                    return self.template('keyholder.mako', whoIsHere=self.visits.reports.whoIsHere(dbConnection))
                else:
                    error = self.visits.scannedMember(dbConnection, bc)
                    if error:
                        cherrypy.log(error)
        return self.station(error)

    @cherrypy.expose
    def admin(self, error=""):
        with self.dbConnect() as dbConnection:
            firstDate = self.visits.reports.getEarliestDate(
                dbConnection).isoformat()
            todayDate = datetime.date.today().isoformat()
            forgotDates = []
            for date in self.visits.reports.getForgottenDates(dbConnection):
                forgotDates.append(date.isoformat())
            teamList = self.visits.teams.getTeamList(dbConnection)
            reportList = self.visits.customReports.get_report_list(
                dbConnection)
        return self.template('admin.mako', forgotDates=forgotDates,
                             firstDate=firstDate, todayDate=todayDate,
                             teamList=teamList, reportList=reportList, error=error)

    @cherrypy.expose
    def reports(self, startDate, endDate):
        return self.template('reports.mako', stats=self.visits.reports.getStats(self.dbConnect(), startDate, endDate))

    @cherrypy.expose
    def createTeam(self, team_name):
        error = self.visits.teams.createTeam(
            self.dbConnect(), team_name)
        return self.admin(error)

    @cherrypy.expose
    def addTeamMembers(self, team_id, students, mentors, coaches):
        listStudents = students.split()
        listMentors = mentors.split()
        listCoaches = coaches.split()

        with self.dbConnect() as dbConnection:
            self.visits.teams.addTeamMembers(
                dbConnection, team_id, listStudents, listMentors, listCoaches)

            return self.team(team_id)

    @cherrypy.expose
    def teamCertifications(self, team_id):
        message = 'Certifications for team: ' + \
            self.visits.teams.team_name_from_id(team_id)
        team_barcodes = self.visits.teams.get_team_members(team_id)
        barcodes = [member.barcode for member in team_barcodes]
        return self.showCertifications(message, barcodes, self.visits.certifications.getAllTools())

    @cherrypy.expose
    def teamAttendance(self, team_id, date, startTime, endTime):
        with self.dbConnect() as dbConnection:
            firstDate = self.visits.reports.getEarliestDate(
                dbConnection).isoformat()
            todayDate = datetime.date.today().isoformat()
            team_name = self.visits.teams.teamNameFromId(dbConnection, team_id)
            datePieces = date.split('-')
            startTimePieces = startTime.split(':')
            endTimePieces = endTime.split(':')

            beginMeetingTime = datetime.datetime.combine(
                datetime.date(int(datePieces[0]), int(
                    datePieces[1]), int(datePieces[2])),
                datetime.time(int(startTimePieces[0]), int(startTimePieces[1])))

            endMeetingTime = datetime.datetime.combine(
                datetime.date(int(datePieces[0]), int(
                    datePieces[1]), int(datePieces[2])),
                datetime.time(int(endTimePieces[0]), int(endTimePieces[1])))

            membersHere = self.visits.reports.whichTeamMembersHere(dbConnection, team_id,
                                                                   beginMeetingTime,
                                                                   endMeetingTime)

        return self.template('team_attendance.mako', team_id=team_id,
                             team_name=team_name, firstDate=firstDate,
                             todayDate=todayDate, membersHere=membersHere,
                             date=date, startTime=startTime, endTime=endTime)

    @cherrypy.expose
    def team(self, team_id, error=''):
        with self.dbConnect() as dbConnection:
            firstDate = self.visits.reports.getEarliestDate(
                dbConnection).isoformat()
            todayDate = datetime.date.today().isoformat()
            team_name = self.visits.teams.teamNameFromId(
                dbConnection, team_id)
            members = self.visits.teams.getTeamMembers(dbConnection, team_id)

        return self.template('team.mako', firstDate=firstDate, team_id=team_id,
                             todayDate=todayDate, team_name=team_name, members=members, error=error)

    @cherrypy.expose
    def reportGraph(self, startDate, endDate):
        cherrypy.response.headers['Content-Type'] = "image/png"
        stats = self.visits.reports.getStats(
            self.dbConnect(), startDate, endDate)
        return stats.getBuildingUsageGraph()

    @cherrypy.expose
    def saveReport(self, sql, report_name):
        error = self.visits.customReports.saveCustomSQL(
            self.dbConnect(), sql, report_name)
        return self.admin(error)

    @cherrypy.expose
    def savedReport(self, report_id, error=''):
        title = "Error"
        sql = ""
        try:
            (title, sql, data) = self.visits.customReports.customReport(report_id)
        except sqlite3.OperationalError as e:
            data = repr(e)

        return self.template('customSQL.mako', report_title=title, sql=sql, data=data)

    @cherrypy.expose
    def customSQLReport(self, sql):
        try:
            data = self.visits.customReports.customSQL(sql)
        except sqlite3.OperationalError as e:
            data = repr(e)

        return self.template('customSQL.mako', sql=sql, data=data)

    @cherrypy.expose
    def bulkAddMembers(self, csvfile):
        error = self.visits.members.bulkAdd(self.dbConnect(), csvfile)
        return self.admin(error)

    @cherrypy.expose
    def addGuest(self, first, last, email, reason, other_reason, newsletter):
        if first == '' or last == '':
            return self.showGuestPage('Need a first and last name')

        displayName = first + ' ' + last[0] + '.'
        with self.dbConnect() as dbConnection:
            if reason != '':
                guest_id = self.visits.guests.add(dbConnection,
                                                  displayName, first, last, email, reason, newsletter)
            else:
                guest_id = self.visits.guests.add(dbConnection,
                                                  displayName, first, last, email, 'Other: ' + other_reason, newsletter)
            self.visits.enterGuest(dbConnection, guest_id)
            return self.showGuestPage('Welcome ' + displayName + '  We are glad you are here!')

    @cherrypy.expose
    def fixData(self, date):
        data = self.visits.reports.getData(self.dbConnect(), date)
        return self.template('fixData.mako', date=date, data=data)

    @cherrypy.expose
    def oops(self):
        self.visits.oopsForgot(self.dbConnect())
        return self.admin('Oops is fixed. :-)')

    @cherrypy.expose
    def fixed(self, output):
        self.visits.fix(self.dbConnect(), output)
        return self.admin()

    @cherrypy.expose
    def guests(self):
        return self.showGuestPage('')

    @cherrypy.expose
    def leaveGuest(self, guest_id):
        with self.dbConnect() as dbConnection:
            self.visits.leaveGuest(dbConnection, guest_id)
            (error, name) = self.visits.guests.getName(dbConnection, guest_id)
        if error:
            return self.showGuestPage(error)

        return self.showGuestPage('Goodbye ' + name + ' We hope to see you again soon!')

    @cherrypy.expose
    def returnGuest(self, guest_id):
        with self.dbConnect() as dbConnection:
            self.visits.enterGuest(dbConnection, guest_id)
            (error, name) = self.visits.guests.getName(dbConnection, guest_id)
            if error:
                return self.showGuestPage(error)

        return self.showGuestPage('Welcome back, ' + name + ' We are glad you are here!')

    @cherrypy.expose
    def certify(self, certifier_id):
        message = ''
        with self.dbConnect() as dbConnection:
            return self.template('certify.mako', message=message,
                                 certifier=self.visits.members.getName(dbConnection,
                                                                       certifier_id)[1],
                                 certifier_id=certifier_id,
                                 members_in_building=self.visits.getMembersInBuilding(
                                     dbConnection),
                                 tools=self.visits.certifications.getToolList(dbConnection, certifier_id))

    @cherrypy.expose
    def certify_all(self, certifier_id):
        message = ''
        return self.template('certify.mako', message=message,
                             certifier=self.visits.members.getName(
                                 certifier_id)[1],
                             certifier_id=certifier_id,
                             members_in_building=self.visits.getAllMembers(),
                             tools=self.visits.certifications.getToolList(certifier_id))

    @cherrypy.expose
    def addCertification(self, member_id, certifier_id, tool_id, level):
        # We don't check here for valid tool since someone is forging HTML to put an invalid one
        # and we'll catch it with the email out...
        self.visits.certifications.addNewCertification(self.dbConnect(),
                                                       member_id, tool_id, level, certifier_id)

        return self.template('congrats.mako', message='',
                             certifier_id=certifier_id,
                             memberName=self.visits.members.getName(member_id)[
                                 1],
                             level=self.visits.certifications.getLevelName(
                                 level),
                             tool=self.visits.certifications.getToolName(tool_id))

    @cherrypy.expose
    def certification_list(self):
        message = ''
        with self.dbConnect() as dbConnection:
            return self.template('certifications.mako', message=message,
                                 barcodes=self.visits.getMemberBarcodesInBuilding(
                                     dbConnection),
                                 tools=self.visits.certifications.getAllTools(
                                     dbConnection),
                                 members=self.visits.members,
                                 certifications=self.visits.certifications.getUserList(dbConnection))

    @cherrypy.expose
    def certification_list_tools(self, tools):
        return self.certification_list_monitor(tools, "0", "True")

    @cherrypy.expose
    def certification_list_monitor(self, tools, start_row, show_table_header):
        message = ''
        barcodes = self.visits.getMemberBarcodesInBuilding(dbConnection)
        start = int(start_row)
        if start <= len(barcodes):
            barcodes = barcodes[start:]
        else:
            barcodes = None
        if show_table_header == '0' or show_table_header.upper() == 'FALSE':
            show_table_header = False

        return self.template('certifications.mako', message=message,
                                 barcodes=barcodes,
                                 tools=self.visits.certifications.getToolsFromList(dbConnection,
                                                                                   tools),
                                 members=self.visits.members,
                                 certifications=self.visits.certifications.getUserList(dbConnection))
    @cherrypy.expose
    def all_certification_list(self):
        message = ''
        with self.dbConnect() as dbConnection:
            return self.template('certifications.mako', message=message,
                                 barcodes=None,
                                 tools=self.visits.certifications.getAllTools(
                                     dbConnection),
                                 members=self.visits.members,
                                 certifications=self.visits.certifications.getUserList(dbConnection))

    @cherrypy.expose
    def index(self):
        return self.who_is_here()

    @cherrypy.expose
    def import_csv(self):
        with self.dbConnect() as dbConnection:
            self.visits.certifications.importFromCSV(dbConnection,
                                                     "students.csv", self.visits.members, sqlite3.connect(self.visits.members.database))
            self.visits.certifications.importFromCSV(dbConnection,
                                                     "adults.csv", self.visits.members, sqlite3.connect(self.visits.members.database))
        return self.all_certification_list()


if __name__ == '__main__':  # pragma no cover
    parser = argparse.ArgumentParser(
        description="CheckMeIn - building check in and out system")
    parser.add_argument('conf')
    args = parser.parse_args()

    # wd = cherrypy.process.plugins.BackgroundTask(15, func)
    # wd.start()

    cherrypy.quickstart(CheckMeIn(), '', args.conf)
