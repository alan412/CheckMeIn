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
                        self.checkout(bc, called=True)
                    else:
                        return self.template('keyholder.mako', whoIsHere=whoIsHere)
                else:
                    error = self.engine.visits.scannedMember(dbConnection, bc)
                    if not current_keyholder_bc:
                        self.engine.accounts.setActiveKeyholder(
                            dbConnection, bc)
                    if error:
                        cherrypy.log(error)
        raise cherrypy.HTTPRedirect("/station")

    @cherrypy.expose
    def checkin(self, barcode, called=False):
        inBarcodeList = barcode.split()
        with self.dbConnect() as dbConnection:
            self.engine.checkin(dbConnection, inBarcodeList)
        if not called:
            raise cherrypy.HTTPRedirect(f"/links?barcode={inBarcodeList[0]}")

    @cherrypy.expose
    def checkout(self, barcode, called=False):
        outBarcodeList = barcode.split()
        with self.dbConnect() as dbConnection:
            (current_keyholder_bc, _) = self.engine.accounts.getActiveKeyholder(
                dbConnection)
            leaving_keyholder_bc = self.engine.checkout(
                dbConnection, current_keyholder_bc, outBarcodeList)

        with self.dbConnect() as dbConnection:
            if leaving_keyholder_bc:
                self.engine.visits.emptyBuilding(
                    dbConnection, leaving_keyholder_bc)
                self.engine.accounts.removeKeyholder(dbConnection)
        if not called:
            raise cherrypy.HTTPRedirect(f"/links?barcode={outBarcodeList[0]}")

    @cherrypy.expose
    def bulkUpdate(self, inBarcodes="", outBarcodes=""):
        self.checkin(inBarcodes, called=True)
        self.checkout(outBarcodes, called=True)
        return "Bulk Update success"

    @cherrypy.expose
    def makeKeyholder(self, barcode):
        error = ''
        bc = barcode.strip()
        with self.dbConnect() as dbConnection:
            self.engine.visits.checkInMember(
                dbConnection, barcode)  # make sure checked in
            result = self.engine.accounts.setActiveKeyholder(
                dbConnection, barcode)
            whoIsHere = self.engine.reports.whoIsHere(dbConnection)

            if result == False:
                return self.template('keyholder.mako', whoIsHere=whoIsHere)
        raise cherrypy.HTTPRedirect(f"/links?barcode={bc}")

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
