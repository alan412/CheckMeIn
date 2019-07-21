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
        self.visits = Visits(DB_STRING, 'data/members.csv',
                             'TFI Barcode', 'TFI Display Name')

    def template(self, name, **kwargs):
        return self.lookup.get_template(name).render(**kwargs)

    def showGuestPage(self, message=''):
        all_guests = self.visits.guests.getList()
        building_guests = self.visits.reports.guestsInBuilding()

        guests_not_here = [
            guest for guest in all_guests if guest not in building_guests]

        return self.template('guests.mako', message=message,
                             inBuilding=building_guests,
                             guestList=guests_not_here)

    @cherrypy.expose
    def station(self, error=''):
        self.visits.checkBuilding()
        return self.template('station.mako',
                             todaysTransactions=self.visits.reports.transactionsToday(),
                             numberPresent=self.visits.reports.numberPresent(),
                             uniqueVisitorsToday=self.visits.reports.uniqueVisitorsToday(),
                             keyholder_name=self.visits.getKeyholderName(),
                             error=error)

    @cherrypy.expose
    def who_is_here(self):
        return self.template('who_is_here.mako', now=datetime.datetime.now(),
                             whoIsHere=self.visits.reports.whoIsHere())

    @cherrypy.expose
    def keyholder(self, barcode):
        error = ''
        barcode = barcode.strip()
        if barcode == KEYHOLDER_BARCODE:
            self.visits.emptyBuilding()
        else:
            error = self.visits.setActiveKeyholder(barcode)
            if error:  # TODO after this case is added, remove no cover
                # pragma no cover
                return self.template('keyholder.mako', error=error)
        return self.station()

    @cherrypy.expose
    # later change this to be more ajaxy, but for now...
    def scanned(self, barcode):
        error = ''
# strip whitespace before or after barcode digits (occasionally a space comes before or after
        barcodes = barcode.split()

        for bc in barcodes:
            if (bc == KEYHOLDER_BARCODE) or (
                    bc == self.visits.getActiveKeyholder()):
                return self.template('keyholder.mako', whoIsHere=self.visits.reports.whoIsHere())
            else:
                error = self.visits.scannedMember(bc)
                if error:
                    cherrypy.log(error)
        return self.station(error)

    @cherrypy.expose
    def admin(self, error=""):
        firstDate = self.visits.reports.getEarliestDate().isoformat()
        todayDate = datetime.date.today().isoformat()
        forgotDates = []
        for date in self.visits.reports.getForgottenDates():
            forgotDates.append(date.isoformat())
        teamList = self.visits.teams.get_team_list()
        reportList = self.visits.customReports.get_report_list()
        return self.template('admin.mako', forgotDates=forgotDates,
                             firstDate=firstDate, todayDate=todayDate,
                             teamList=teamList, reportList=reportList, error=error)

    @cherrypy.expose
    def reports(self, startDate, endDate):
        return self.template('reports.mako', stats=self.visits.reports.getStats(startDate, endDate))

    @cherrypy.expose
    def createTeam(self, team_name):
        error = self.visits.teams.create_team(team_name)
        return self.admin(error)

    @cherrypy.expose
    def addTeamMembers(self, team_id, students, mentors, coaches):
        listStudents = students.split()
        listMentors = mentors.split()
        listCoaches = coaches.split()
        fullList = []

        for student in listStudents:
            fullList.append((student, TeamMemberType.student))
        for mentor in listMentors:
            fullList.append((mentor, TeamMemberType.mentor))
        for coach in listCoaches:
            fullList.append((coach, TeamMemberType.coach))

        self.visits.teams.add_team_members(team_id, fullList)

        return self.team(team_id)

    @cherrypy.expose
    def teamAttendance(self, team_id, date, startTime, endTime):
        print("Team Attendance: ", team_id, date, startTime, endTime)
        firstDate = self.visits.reports.getEarliestDate().isoformat()
        todayDate = datetime.date.today().isoformat()
        team_name = self.visits.teams.team_name_from_id(team_id)
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

        membersHere = self.visits.reports.whichTeamMembersHere(team_id,
                                                               beginMeetingTime,
                                                               endMeetingTime)

        return self.template('team_attendance.mako', team_id=team_id,
                             team_name=team_name, firstDate=firstDate,
                             todayDate=todayDate, membersHere=membersHere,
                             date=date, startTime=startTime, endTime=endTime)

    @cherrypy.expose
    def team(self, team_id, error=''):
        firstDate = self.visits.reports.getEarliestDate().isoformat()
        todayDate = datetime.date.today().isoformat()
        team_name = self.visits.teams.team_name_from_id(team_id)
        members = self.visits.teams.get_team_members(team_id)

        return self.template('team.mako', firstDate=firstDate, team_id=team_id,
                             todayDate=todayDate, team_name=team_name, members=members, error=error)

    @cherrypy.expose
    def reportGraph(self, startDate, endDate):
        cherrypy.response.headers['Content-Type'] = "image/png"
        stats = self.visits.reports.getStats(startDate, endDate)
        print(stats)
        return stats.getBuildingUsageGraph()

    @cherrypy.expose
    def saveReport(self, sql, report_name):
        error = self.visits.customReports.saveCustomSQL(sql, report_name)
        return self.admin(error)

    @cherrypy.expose
    def savedReport(self, report_id, error=''):
        title = "Error"
        sql = ""
        try:
            (title, sql, data) = self.visits.customReports.customReport(report_id)
            print("Title: ", title)
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
    def addMember(self, display, barcode):
        error = self.visits.members.add(display, barcode)
        return self.admin(error)

    @cherrypy.expose
    def addGuest(self, first, last, email, reason, other_reason, newsletter):
        if first == '' or last == '':
            return self.showGuestPage('Need a first and last name')

        displayName = first + ' ' + last[0] + '.'
        if reason != '':
            guest_id = self.visits.guests.add(
                displayName, first, last, email, reason, newsletter)
        else:
            guest_id = self.visits.guests.add(
                displayName, first, last, email, 'Other: ' + other_reason, newsletter)
        self.visits.enterGuest(guest_id)
        return self.showGuestPage('Welcome ' + displayName + '  We are glad you are here!')

    @cherrypy.expose
    def fixData(self, date):
        data = self.visits.reports.getData(date)
        return self.template('fixData.mako', date=date, data=data)

    @cherrypy.expose
    def oops(self):
        self.visits.oopsForgot()
        return self.admin('Oops is fixed. :-)')

    @cherrypy.expose
    def fixed(self, output):
        self.visits.fix(output)
        return self.admin()

    @cherrypy.expose
    def guests(self):
        return self.showGuestPage('')

    @cherrypy.expose
    def leaveGuest(self, guest_id):
        self.visits.leaveGuest(guest_id)
        (error, name) = self.visits.guests.getName(guest_id)
        if error:
            return self.showGuestPage(error)

        return self.showGuestPage('Goodbye ' + name + ' We hope to see you again soon!')

    @cherrypy.expose
    def returnGuest(self, guest_id):
        self.visits.enterGuest(guest_id)
        (error, name) = self.visits.guests.getName(guest_id)
        if error:
            return self.showGuestPage(error)

        return self.showGuestPage('Welcome back, ' + name + ' We are glad you are here!')

    @cherrypy.expose
    def submitCertification(self, member_id, tool_id, certifier_id, newLevel):
        todayDate = datetime.date.today().isoformat()
        if self.visits.certification.addCertification(dbConnection, member_id, tool_id, newLevel, todayDate, certifier_id):
            message = 'Success adding'
        else:
            message = 'Failure adding'
        return self.template('certifications.mako', message=message,
                             certifications=self.visits.certifications)

    @cherrypy.expose
    def certify(self, certifier_id):
        message = ''
        return self.template('certify.mako', message=message,
                             certifier=self.visits.members.getName(
                                 certifier_id)[1],
                             certifier_id=certifier_id,
                             members_in_building=self.visits.getMembersInBuilding(),
                             tools=self.visits.certifications.getToolList(certifier_id))

    @cherrypy.expose
    def addCertification(self, member_id, certifier_id, tool_id, level):
        # We don't check here for valid tool since someone is forging HTML to put an invalid one
        # and we'll catch it with the email out...
        self.visits.certifications.addNewCertification(
            member_id, tool_id, level, certifier_id)

        return self.certification_list()

    @cherrypy.expose
    def certification_list(self):
        message = ''
        return self.template('certifications.mako', message=message,
                             barcodes=self.visits.getMemberBarcodesInBuilding(),
                             tools=self.visits.certifications.getAllTools(),
                             members=self.visits.members,
                             certifications=self.visits.certifications.getUserList())

    @cherrypy.expose
    def all_certification_list(self):
        message = ''
        return self.template('certifications.mako', message=message,
                             barcodes=None,
                             tools=self.visits.certifications.getAllTools(),
                             members=self.visits.members,
                             certifications=self.visits.certifications.getUserList())

    @cherrypy.expose
    def index(self):
        return self.who_is_here()


def func():
    print("Test")


if __name__ == '__main__':  # pragma no cover
    parser = argparse.ArgumentParser(
        description="CheckMeIn - building check in and out system")
    parser.add_argument('conf')
    args = parser.parse_args()

    # wd = cherrypy.process.plugins.BackgroundTask(15, func)
    # wd.start()

    cherrypy.quickstart(CheckMeIn(), '', args.conf)
