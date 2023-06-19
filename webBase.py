import datetime
import cherrypy
from accounts import Role


class Cookie(object):
    def __init__(self, name):
        self.name = name

    def get(self, default=''):
        result = default
        result = cherrypy.session.get(self.name)
        if not result:
            self.set(default)
            result = default

        return result

    def set(self, value):
        cherrypy.session[self.name] = value
        return value

    def delete(self):
        cherrypy.session.pop(self.name, None)


class WebBase(object):
    def __init__(self, lookup, engine):
        self.lookup = lookup
        self.engine = engine

    def template(self, name, **kwargs):
        barcode = self.getBarcodeNoLogin()
        logoLink = f'/links/?barcode={barcode}' if barcode else f'/links/'

        return self.lookup.get_template(name).render(logoLink=logoLink, **kwargs)

    def dbConnect(self):
        return self.engine.dbConnect()

    def getBarcode(self, source):
        return self.getCookie('barcode', source)

    def getUser(self, source):
        return self.getCookie('username', source)

    def checkPermissions(self, roleCheck, source):
        if self.hasPermissionsNologin(roleCheck):
            return
        Cookie('source').set(source)
        raise cherrypy.HTTPRedirect("/profile/login")

    def hasPermissionsNologin(self, roleCheck):
        role = Role(Cookie('role').get(0))
        return role.getValue() & roleCheck

    def getRole(self, source):
        return Role(self.getCookie('role', source))

    def getCookie(self, cookie, source):
        value = Cookie(cookie).get('')
        if not value:
            Cookie('source').set(source)
            raise cherrypy.HTTPRedirect("/profile/login")
        return value

    def getBarcodeNoLogin(self):
        return Cookie('barcode').get(None)

    def dateFromString(self, inputStr):
        return datetime.datetime(int(inputStr[0:4]),
                                 int(inputStr[5:7]),
                                 int(inputStr[8:10])).replace(
            hour=0, minute=0, second=0, microsecond=0)
