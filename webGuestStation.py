import cherrypy
from webBase import WebBase
import utils


class WebGuestStation(WebBase):
    # Guest Pages
    def showGuestPage(self, message=''):
        with self.dbConnect() as dbConnection:
            (building_guests, recent_guests_not_here) = self.engine.getGuestLists(
                dbConnection)

        return self.template('guests.mako', message=message,
                             inBuilding=building_guests,
                             guestList=recent_guests_not_here)

    @cherrypy.expose
    def addGuest(self, first, last, email, reason, other_reason, newsletter):
        if first == '' or last == '':
            return self.showGuestPage('Need a first and last name')
        if len(first) > 32:
            return self.showGuestPage('First name limited to 32 characters')

        displayName = first + ' ' + last[0] + '.'
        with self.dbConnect() as dbConnection:
            if reason != '':
                guest_id = self.engine.guests.add(dbConnection,
                                                  displayName, first, last, email, reason, newsletter)
            else:
                guest_id = self.engine.guests.add(dbConnection,
                                                  displayName, first, last, email, 'Other: ' + other_reason, newsletter)
            self.engine.visits.enterGuest(dbConnection, guest_id)
            return self.showGuestPage('Welcome ' + displayName + '  We are glad you are here!')

    @cherrypy.expose
    def index(self):
        return self.showGuestPage('')

    @cherrypy.expose
    def leaveGuest(self, guest_id, comments=""):
        with self.dbConnect() as dbConnection:
            self.engine.visits.leaveGuest(dbConnection, guest_id)
            (error, name) = self.engine.guests.getName(dbConnection, guest_id)
        if error:
            return self.showGuestPage(error)

        if comments:
            (error, email) = self.engine.guests.getEmail(dbConnection, guest_id)
            utils.sendEmail('TFI Ops', 'tfi-ops@googlegroups.com', 'Comments from ' + name,
                            'Comments left:\n' + comments, name, email)

        return self.showGuestPage('Goodbye ' + name + ' We hope to see you again soon!')

    @cherrypy.expose
    def returnGuest(self, guest_id):
        with self.dbConnect() as dbConnection:
            self.engine.visits.enterGuest(dbConnection, guest_id)
            (error, name) = self.engine.guests.getName(dbConnection, guest_id)
            if error:
                return self.showGuestPage(error)

        return self.showGuestPage('Welcome back, ' + name + ' We are glad you are here!')
