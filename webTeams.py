import datetime
from teams import TeamMemberType
import cherrypy
from webBase import WebBase, Cookie
from accounts import Role


class WebTeams(WebBase):
    def __init__(self, lookup, engine):
        super().__init__(lookup, engine)
# Teams

    def checkPermissions(self, team_id):
        source = "/teams?team_id="+team_id
        role = self.getRole(source)
        if role.getValue() & Role.ADMIN:
            return
        if not role.getValue() & Role.COACH:
            Cookie('source').set(source)
            raise cherrypy.HTTPRedirect("/profile/login")
        coachTeam = Cookie('coach-' + str(team_id)).get(
            self.engine.teams.isCoachOfTeam(
                self.dbConnect(), team_id, self.getBarcode(''))
        )
        if not coachTeam:
            Cookie('source').set(source)
            raise cherrypy.HTTPRedirect("/profile/login")

    @cherrypy.expose
    def certifications(self, team_id):
        raise cherrypy.HTTPRedirect("/certifications/team?team_id="+team_id)

    @cherrypy.expose
    def attendance(self, team_id, date, startTime, endTime):
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
        self.checkPermissions(team_id)
        if not team_id:
            raise cherrypy.HTTPRedirect("/admin/teams")
        with self.dbConnect() as dbConnection:
            teamInfo = self.engine.teams.fromTeamId(dbConnection, team_id)
            firstDate = teamInfo.startDate
            todayDate = datetime.date.today().isoformat()

            members = self.engine.teams.getTeamMembers(dbConnection, team_id)
            activeMembers = self.engine.members.getActive(dbConnection)
            seasons = self.engine.teams.getAllSeasons(dbConnection, teamInfo)

        return self.template('team.mako', firstDate=firstDate, team_id=team_id,
                             seasons=seasons,
                             username=Cookie('username').get(''),
                             todayDate=todayDate, team_name=teamInfo.name,
                             members=members, activeMembers=activeMembers,
                             TeamMemberType=TeamMemberType, error="")

    @cherrypy.expose
    def addMember(self, team_id, type, member=None):
        if member:
            self.checkPermissions(team_id)
            with self.dbConnect() as dbConnection:
                self.engine.teams.addMember(
                    dbConnection, team_id, member, type)

        raise cherrypy.HTTPRedirect("/teams?team_id="+team_id)

    @cherrypy.expose
    def removeMember(self, team_id, member):
        self.checkPermissions(team_id)
        with self.dbConnect() as dbConnection:
            self.engine.teams.removeMember(dbConnection, team_id, member)

        raise cherrypy.HTTPRedirect("/teams?team_id="+team_id)

    @cherrypy.expose
    def renameTeam(self, team_id, newName):
        self.checkPermissions(team_id)
        with self.dbConnect() as dbConnection:
            self.engine.teams.renameTeam(dbConnection, team_id, newName)

        raise cherrypy.HTTPRedirect("/teams?team_id="+team_id)

    @cherrypy.expose
    def newSeason(self, team_id, startDate, **returning):
        self.checkPermissions(team_id)
        with self.dbConnect() as dbConnection:
            teamInfo = self.engine.teams.fromTeamId(dbConnection, team_id)
            seasonStart = self.dateFromString(startDate)
            self.engine.teams.createTeam(dbConnection,
                                         teamInfo.programName, teamInfo.programNumber, teamInfo.name, seasonStart)
        with self.dbConnect() as dbConnection:
            teamInfo = self.engine.teams.getTeamFromProgramInfo(
                dbConnection, teamInfo.programName, teamInfo.programNumber)

            for member, value in returning.items():
                self.engine.teams.addMember(
                    dbConnection, teamInfo.teamId, member, int(value))
        raise cherrypy.HTTPRedirect("/teams?team_id="+str(teamInfo.teamId))

    @cherrypy.expose
    def update(self, team_id, **params):
        self.checkPermissions(team_id)
        checkIn = []
        checkOut = []
        for param, value in params.items():
            if value == 'in':
                checkIn.append(param)
            else:
                checkOut.append(param)

        with self.dbConnect() as dbConnection:
            leaving_keyholder_bc = self.engine.bulkUpdate(
                dbConnection, checkIn, checkOut)

        with self.dbConnect() as dbConnection:
            if leaving_keyholder_bc:
                whoIsHere = self.engine.reports.whoIsHere(dbConnection)
                if len(whoIsHere) > 1:
                    return self.template('keyholderCheckout.mako', barcode=leaving_keyholder_bc, whoIsHere=whoIsHere)
                self.engine.accounts.removeKeyholder(dbConnection)
                error = self.engine.visits.checkOutMember(
                    dbConnection, leaving_keyholder_bc)

        raise cherrypy.HTTPRedirect("/teams?team_id="+team_id)
