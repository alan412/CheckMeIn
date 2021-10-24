from accounts import Accounts, Role
import cherrypy
from webBase import WebBase

KEYHOLDER_BARCODE = '999901'


class WebMainStation(WebBase):
    # STATION
    @cherrypy.expose
    def index(self, error=''):
        with self.dbConnect() as dbConnection:
            (_, keyholder_name) = self.engine.accounts.getActiveKeyholder(dbConnection)

            return self.template('station.mako',
                                 todaysTransactions=self.engine.reports.transactionsToday(
                                     dbConnection),
                                 numberPresent=self.engine.reports.numberPresent(
                                     dbConnection),
                                 uniqueVisitorsToday=self.engine.reports.uniqueVisitorsToday(
                                     dbConnection),
                                 keyholder_name=keyholder_name,
                                 stewards=self.engine.accounts.getPresentWithRole(
                                     dbConnection, Role.SHOP_STEWARD),
                                 error=error)

    @cherrypy.expose
    # later change this to be more ajaxy, but for now...
    def scanned(self, barcode):
        error = ''
# strip whitespace before or after barcode digits (occasionally a space comes before or after)
        barcodes = barcode.split()
        with self.dbConnect() as dbConnection:
            (current_keyholder_bc, _) = self.engine.accounts.getActiveKeyholder(
                dbConnection)
            for bc in barcodes:
                if (bc == KEYHOLDER_BARCODE) or (bc == current_keyholder_bc):
                    whoIsHere = self.engine.reports.whoIsHere(dbConnection)
                    if (bc == current_keyholder_bc) and len(whoIsHere) == 1:
                        self.checkout(bc)
                    return self.template('keyholder.mako', whoIsHere=self.engine.reports.whoIsHere(dbConnection))
                else:
                    error = self.engine.visits.scannedMember(dbConnection, bc)
                    if not current_keyholder_bc:
                        self.engine.accounts.setActiveKeyholder(
                            dbConnection, bc)
                    if error:
                        cherrypy.log(error)
        raise cherrypy.HTTPRedirect("/station")

    @cherrypy.expose
    def checkin(self, barcode):
        return self.bulkUpdate(inBarcodes=barcode)

    @cherrypy.expose
    def checkout(self, barcode):
        return self.bulkUpdate(outBarcodes=barcode)

    @cherrypy.expose
    def bulkUpdate(self, inBarcodes="", outBarcodes=""):
        inBarcodeList = inBarcodes.split()
        outBarcodeList = outBarcodes.split()
        currentKeyholderLeaving = False
        with self.dbConnect() as dbConnection:
            (current_keyholder_bc, _) = self.engine.accounts.getActiveKeyholder(
                dbConnection)
            for barcode in inBarcodeList:
                error = self.engine.visits.checkInMember(dbConnection, barcode)
                if not current_keyholder_bc:
                    self.engine.accounts.setActiveKeyholder(
                        dbConnection, barcode)
            for barcode in outBarcodeList:
                if barcode == current_keyholder_bc:
                    currentKeyholderLeaving = True
                else:
                    error = self.engine.visits.checkOutMember(
                        dbConnection, barcode)
        with self.dbConnect() as dbConnection:
            if currentKeyholderLeaving:
                self.engine.visits.emptyBuilding(
                    dbConnection, current_keyholder_bc)
                self.engine.accounts.removeKeyholder(dbConnection)
        raise cherrypy.HTTPRedirect("/station")

    @cherrypy.expose
    def makeKeyholder(self, barcode):
        error = ''
        bc = barcode.strip()
        with self.dbConnect() as dbConnection:
            self.engine.visits.checkInMember(
                dbConnection, barcode)  # make sure checked in
            error = self.engine.accounts.setActiveKeyholder(
                dbConnection, barcode)
            if error:  # pragma: no cover # TODO after this case is added, remove no cover
                return self.template('keyholder.mako', error=error)
        raise cherrypy.HTTPRedirect("/station")

    @cherrypy.expose
    def keyholder(self, barcode):
        error = ''
        bc = barcode.strip()
        with self.dbConnect() as dbConnection:
            (current_keyholder_bc, _) = self.engine.accounts.getActiveKeyholder(
                dbConnection)
            if (bc == KEYHOLDER_BARCODE) or (bc == current_keyholder_bc):
                self.engine.visits.emptyBuilding(
                    dbConnection, current_keyholder_bc)
                self.engine.accounts.removeKeyholder(dbConnection)
            else:
                return self.makeKeyholder(barcode)

        raise cherrypy.HTTPRedirect("/station")
