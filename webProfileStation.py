import datetime
import cherrypy
from accounts import Accounts, Role
from webBase import WebBase, Cookie


class WebProfileStation(WebBase):
    def getBarcode(self):
        barcode = Cookie('barcode').get('')
        if not barcode:
            raise cherrypy.HTTPRedirect("/profile/login")
        return barcode

    @cherrypy.expose
    def logout(self):
        Cookie('username').delete()
        Cookie('barcode').delete()
        Cookie('role').delete()
        raise cherrypy.HTTPRedirect("/profile/login")

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
        raise cherrypy.HTTPRedirect("/profile")

    # Admin
    @cherrypy.expose
    def index(self, error=""):
        barcode = self.getBarcode()
        with self.dbConnect() as dbConnection:
            devices = self.engine.devices.getList(dbConnection, barcode)
        return self.template('profile.mako', error='', username=Cookie('username').get(''), devices=devices)

    @cherrypy.expose
    def forgotPassword(self, user):
        with self.dbConnect() as dbConnection:
            self.engine.accounts.forgotPassword(dbConnection, user)
        return "You have been e-mailed a way to reset your password.  It will only be good for 24 hours."

    @cherrypy.expose
    def resetPasswordToken(self, user, token):
        return self.template('newPassword.mako', error='', user=user, token=token)

    @cherrypy.expose
    def newPassword(self, user, token, newPass1, newPass2):
        if newPass1 != newPass2:
            return self.template('newPassword.mako', error='Passwords must match', user=user, token=token)
        if self.verify_forgot(user, token, newPass1):
            raise cherrypy.HTTPRedirect("/profile/login")
        return self.forgotPassword(user)

    @cherrypy.expose
    def profile(self):
        barcode = self.getBarcode()
        with self.dbConnect() as dbConnection:
            devices = self.engine.devices.getList(dbConnection, barcode)
        return self.template('profile.mako', error='', user=Cookie('user'.get(''), devices=devices))

    @cherrypy.expose
    def addDevice(self, mac, name):
        barcode = self.getBarcode()

        with self.dbConnect() as dbConnection:
            devices = self.engine.devices.add(dbConnection, mac, name, barcode)
        raise cherrypy.HTTPRedirect("/profile")

    @cherrypy.expose
    def delDevice(self, mac):
        barcode = self.getBarcode()
        with self.dbConnect() as dbConnection:
            devices = self.engine.devices.delete(dbConnection, mac, barcode)
        raise cherrypy.HTTPRedirect("/profile")
