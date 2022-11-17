import datetime
import cherrypy
from accounts import Accounts, Role
from webBase import WebBase, Cookie


class WebProfile(WebBase):

    @cherrypy.expose
    def logout(self):
        barcode = Cookie('barcode').get()
        Cookie('username').delete()
        Cookie('barcode').delete()
        Cookie('role').delete()
        raise cherrypy.HTTPRedirect(f"/links?barcode={barcode}")

    @cherrypy.expose
    def login(self, error=""):
        return self.template('login.mako', error=error)

    @cherrypy.expose
    def loginAttempt(self, username, password):
        with self.dbConnect() as dbConnection:
            (barcode, role) = self.engine.accounts.getBarcode(
                dbConnection, username, password)
            if not barcode:
                return self.template('login.mako', error="Invalid username/password")
            Cookie('barcode').set(barcode)
            Cookie('username').set(username)
            Cookie('role').set(role.getValue())
        dest = Cookie('source').get(f"/links?barcode={barcode}")
        Cookie('source').delete()
        raise cherrypy.HTTPRedirect(dest)

    # Profile
    @cherrypy.expose
    def index(self, error=""):
        barcode = self.getBarcode('/profile')
        with self.dbConnect() as dbConnection:
            devices = self.engine.devices.getList(dbConnection, barcode)
        return self.template('profile.mako', error='', username=Cookie('username').get(''), devices=devices)

    @cherrypy.expose
    def forgotPassword(self, user):
        with self.dbConnect() as dbConnection:
            email = self.engine.accounts.forgotPassword(
                dbConnection, user)
            self.engine.logEvents.addEvent(
                dbConnection,
                "Forgot password request", f"{email} for {user}")
        return "You have been e-mailed a way to reset your password.  It will only be good for 24 hours."

    @cherrypy.expose
    def resetPasswordToken(self, user, token):
        return self.template('newPassword.mako', error='', user=user, token=token)

    @cherrypy.expose
    def newPassword(self, user, token, newPass1, newPass2):
        if newPass1 != newPass2:
            return self.template('newPassword.mako', error='Passwords must match', user=user, token=token)
        with self.dbConnect() as dbConnection:
            worked = self.engine.accounts.verify_forgot(
                dbConnection, user, token, newPass1)
        if worked:
            raise cherrypy.HTTPRedirect("/profile/login")
        return "Token not correct.  Try link again"

    @cherrypy.expose
    def changePassword(self, oldPass, newPass1, newPass2):
        user = self.getUser('/profile')
        if newPass1 != newPass2:
            error = "New Passwords must match"
        else:
            with self.dbConnect() as dbConnection:
                barcode = self.engine.accounts.getBarcode(
                    dbConnection, user, oldPass)
                if barcode:
                    self.engine.accounts.changePassword(
                        dbConnection, user, oldPass, newPass1)
                    error = ""
                else:
                    error = "Incorrect password"
        return self.index(error)

    @cherrypy.expose
    def addDevice(self, mac, name):
        barcode = self.getBarcode('/profile')

        with self.dbConnect() as dbConnection:
            devices = self.engine.devices.add(dbConnection, mac, name, barcode)
        raise cherrypy.HTTPRedirect("/profile")

    @cherrypy.expose
    def delDevice(self, mac):
        barcode = self.getBarcode('/profile')
        with self.dbConnect() as dbConnection:
            devices = self.engine.devices.delete(dbConnection, mac, barcode)
        raise cherrypy.HTTPRedirect("/profile")
