import argparse
import datetime
from mako.lookup import TemplateLookup
import cherrypy
import cherrypy.process.plugins

import engine
from webBase import WebBase
from webMainStation import WebMainStation
from webGuestStation import WebGuestStation
from webCertifications import WebCertifications
from webTeams import WebTeams
from webAdminStation import WebAdminStation
from webReports import WebReports

DB_STRING = 'data/checkMeIn.db'


class CheckMeIn(WebBase):
    def __init__(self):
        self.lookup = TemplateLookup(
            directories=['HTMLTemplates'], default_filters=['h'])
        self.engine = engine.Engine(DB_STRING)
        super().__init__(self.lookup, self.engine)
        self.station = WebMainStation(self.lookup, self.engine)
        self.guests = WebGuestStation(self.lookup, self.engine)
        self.certification = WebCertifications(self.lookup, self.engine)
        self.teams = WebTeams(self.lookup, self.engine)
        self.admin = WebAdminStation(self.lookup, self.engine)
        self.reports = WebReports(self.lookup, self.engine)

    @cherrypy.expose
    def index(self):
        with self.dbConnect() as dbConnection:
            (_, keyholder_name) = self.engine.keyholders.getActiveKeyholder(dbConnection)
            return self.template('who_is_here.mako',
                                 now=datetime.datetime.now(),
                                 keyholder=keyholder_name,
                                 whoIsHere=self.engine.reports.whoIsHere(dbConnection))


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="CheckMeIn - building check in and out system")
    parser.add_argument('conf')
    args = parser.parse_args()

    # wd = cherrypy.process.plugins.BackgroundTask(15, func)
    # wd.start()

    cherrypy.quickstart(CheckMeIn(), '', args.conf)
