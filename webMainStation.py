import cherrypy
from webBase import WebBase

KEYHOLDER_BARCODE = '999901'


class WebMainStation(WebBase):
    # STATION
    @cherrypy.expose
    def index(self, error=''):
        with self.dbConnect() as dbConnection:
            self.engine.visits.checkBuilding(
                dbConnection)  # TODO - Move to thread

            (_, keyholder_name) = self.engine.keyholders.getActiveKeyholder(dbConnection)

            return self.template('station.mako',
                                 todaysTransactions=self.engine.reports.transactionsToday(
                                     dbConnection),
                                 numberPresent=self.engine.reports.numberPresent(
                                     dbConnection),
                                 uniqueVisitorsToday=self.engine.reports.uniqueVisitorsToday(
                                     dbConnection),
                                 keyholder_name=keyholder_name,
                                 error=error)

    @cherrypy.expose
    # later change this to be more ajaxy, but for now...
    def scanned(self, barcode):
        error = ''
# strip whitespace before or after barcode digits (occasionally a space comes before or after)
        barcodes = barcode.split()
        with self.dbConnect() as dbConnection:
            (current_keyholder_bc, _) = self.engine.keyholders.getActiveKeyholder(
                dbConnection)
            for bc in barcodes:
                if (bc == KEYHOLDER_BARCODE) or (bc == current_keyholder_bc):
                    return self.template('keyholder.mako', whoIsHere=self.engine.reports.whoIsHere(dbConnection))
                else:
                    error = self.engine.visits.scannedMember(dbConnection, bc)
                    if not current_keyholder_bc:
                        self.engine.keyholders.setActiveKeyholder(
                            dbConnection, bc)
                    if error:
                        cherrypy.log(error)
        raise cherrypy.HTTPRedirect("/station")

    @cherrypy.expose
    def keyholder(self, barcode):
        error = ''
        bc = barcode.strip()
        with self.dbConnect() as dbConnection:
            (current_keyholder_bc, _) = self.engine.keyholders.getActiveKeyholder(
                dbConnection)
            if (bc == KEYHOLDER_BARCODE) or (bc == current_keyholder_bc):
                self.engine.visits.emptyBuilding(
                    dbConnection, current_keyholder_bc)
                self.engine.keyholders.removeKeyholder(dbConnection)
            else:
                error = self.engine.keyholders.setActiveKeyholder(
                    dbConnection, barcode)
                if error:  # pragma: no cover # TODO after this case is added, remove no cover
                    return self.template('keyholder.mako', error=error)
        return self.index()
