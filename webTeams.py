import datetime
from teams import TeamMemberType
import cherrypy
from webBase import WebBase


class WebTeams(WebBase):  # pragma: no cover
    def __init__(self, lookup, engine):
        super().__init__(lookup, engine)
# Teams

    @cherrypy.expose
    def addTeamMembers(self, team_id, students, mentors, coaches):
        listStudents = students.split()
        listMentors = mentors.split()
        listCoaches = coaches.split()

        with self.dbConnect() as dbConnection:
            self.engine.teams.addTeamMembers(
                dbConnection, team_id, listStudents, listMentors, listCoaches)

            return self.team(team_id)

    @cherrypy.expose
    def teamCertifications(self, team_id):
        message = 'Certifications for team: ' + \
            self.engine.teams.team_name_from_id(team_id)
        team_barcodes = self.engine.teams.get_team_members(team_id)
        barcodes = [member.barcode for member in team_barcodes]
        return self.showCertifications(message, barcodes, self.engine.certifications.getAllTools())

    @cherrypy.expose
    def teamAttendance(self, team_id, date, startTime, endTime):
        with self.dbConnect() as dbConnection:
            firstDate = self.engine.reports.getEarliestDate(
                dbConnection).isoformat()
            todayDate = datetime.date.today().isoformat()
            team_name = self.engine.teams.teamNameFromId(dbConnection, team_id)
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

            membersHere = self.engine.reports.whichTeamMembersHere(dbConnection, team_id,
                                                                   beginMeetingTime,
                                                                   endMeetingTime)

        return self.template('team_attendance.mako', team_id=team_id,
                             team_name=team_name, firstDate=firstDate,
                             todayDate=todayDate, membersHere=membersHere,
                             date=date, startTime=startTime, endTime=endTime)

    @cherrypy.expose
    def index(self, team_id="", error=''):
        if not team_id:
            raise cherrypy.HTTPRedirect("/admin/teams")
        with self.dbConnect() as dbConnection:
            firstDate = self.engine.reports.getEarliestDate(
                dbConnection).isoformat()
            todayDate = datetime.date.today().isoformat()
            team_name = self.engine.teams.teamNameFromId(
                dbConnection, team_id)
            members = self.engine.teams.getTeamMembers(dbConnection, team_id)

        return self.template('team.mako', firstDate=firstDate, team_id=team_id,
                             todayDate=todayDate, team_name=team_name, members=members, TeamMemberType=TeamMemberType, error="")

    @cherrypy.expose
    def update(self, team_id, **params):
        checkIn = []
        checkOut = []
        for param, value in params.items():
            if value == 'in':
                checkIn.append(param)
            else:
                checkOut.append(param)

        currentKeyholderLeaving = False
        with self.dbConnect() as dbConnection:
            (current_keyholder_bc, _) = self.engine.accounts.getActiveKeyholder(
                dbConnection)
            for barcode in checkIn:
                error = self.engine.visits.checkInMember(dbConnection, barcode)
                if not current_keyholder_bc:
                    self.engine.accounts.setActiveKeyholder(
                        dbConnection, barcode)
            for barcode in checkOut:
                if barcode == current_keyholder_bc:
                    currentKeyholderLeaving = True
                else:
                    error = self.engine.visits.checkOutMember(
                        dbConnection, barcode)
        with self.dbConnect() as dbConnection:
            if currentKeyholderLeaving:
                whoIsHere = self.engine.reports.whoIsHere(dbConnection)
                if len(whoIsHere) > 1:
                    return self.template('keyholderCheckout.mako', barcode=current_keyholder_bc, whoIsHere=self.engine.reports.whoIsHere(dbConnection))
                self.engine.accounts.removeKeyholder(dbConnection)
                error = self.engine.visits.checkOutMember(
                    dbConnection, current_keyholder_bc)

        raise cherrypy.HTTPRedirect("/teams?team_id="+team_id)
