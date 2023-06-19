import os
import sqlite3

from members import Members
from guests import Guests
from reports import Reports
from teams import Teams
from customReports import CustomReports
from certifications import Certifications
from visits import Visits
from accounts import Accounts
from devices import Devices
from unlocks import Unlocks
from logEvents import LogEvents
from config import Config

SCHEMA_VERSION = 16

# This is the engine for all of the backend


class Engine(object):
    def __init__(self, dbPath, dbName, update):
        self.database = dbPath + dbName
        self.dataPath = dbPath
        self.update = update
        self.visits = Visits()
        self.guests = Guests()
        self.reports = Reports(self)
        self.teams = Teams()
        self.accounts = Accounts()
        self.devices = Devices()
        self.unlocks = Unlocks()
        self.config = Config()
        # needs path since it will open read only
        self.customReports = CustomReports(self.database)
        self.certifications = Certifications()
        self.members = Members()
        self.logEvents = LogEvents()

        if not os.path.exists(self.database):
            if not os.path.exists(dbPath):
                os.mkdir(dbPath)
            with self.dbConnect() as c:
                self.migrate(c, 0)
        else:
            with self.dbConnect() as c:
                data = c.execute('PRAGMA schema_version').fetchone()
                if data[0] != SCHEMA_VERSION:
                    self.migrate(c, data[0])

    def dbConnect(self):
        return sqlite3.connect(self.database,
                               detect_types=sqlite3.PARSE_DECLTYPES)

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version < SCHEMA_VERSION:
            self.config.migrate(dbConnection, db_schema_version)
            self.visits.migrate(dbConnection, db_schema_version)
            self.members.migrate(dbConnection, db_schema_version)
            self.guests.migrate(dbConnection, db_schema_version)
            self.teams.migrate(dbConnection, db_schema_version)
            self.customReports.migrate(dbConnection, db_schema_version)
            self.certifications.migrate(dbConnection, db_schema_version)
            self.accounts.migrate(dbConnection, db_schema_version)
            self.devices.migrate(dbConnection, db_schema_version)
            self.unlocks.migrate(dbConnection, db_schema_version)
            self.logEvents.migrate(dbConnection, db_schema_version)
            dbConnection.execute('PRAGMA schema_version = ' +
                                 str(SCHEMA_VERSION))
        elif db_schema_version != SCHEMA_VERSION:  # pragma: no cover
            raise Exception("Unknown DB schema version" +
                            str(db_schema_version) + ": " + self.database)

    def injectData(self, dictValues):
        areas = {
            "visits": self.visits,
            "members": self.members,
            "guests": self.guests,
            "teams": self.teams,
            "customReports": self.customReports,
            "certifications": self.certifications,
            "accounts": self.accounts,
            "devices": self.devices,
            "unlocks": self.unlocks,
            "logEvents": self.logEvents,
            "config": self.config
        }

        for (key, member) in areas.items():
            if key in dictValues:
                with self.dbConnect() as dbConnection:
                    member.injectData(dbConnection, dictValues[key])

    def getGuestLists(self, dbConnection):
        all_guests = self.guests.getList(dbConnection)

        building_guests = self.reports.guestsInBuilding(dbConnection)

        guests_not_here = [
            guest for guest in all_guests if guest not in building_guests
        ]

        return (building_guests, guests_not_here)

    def checkin(self, dbConnection, check_ins):
        (current_keyholder_bc, _) = self.accounts.getActiveKeyholder(
            dbConnection)
        for barcode in check_ins:
            error = self.visits.checkInMember(dbConnection, barcode)
            if not current_keyholder_bc:
                if self.accounts.setActiveKeyholder(dbConnection, barcode):
                    current_keyholder_bc = barcode
        return current_keyholder_bc

    def checkout(self, dbConnection, current_keyholder_bc, check_outs):
        currentKeyholderLeaving = False
        for barcode in check_outs:
            if barcode == current_keyholder_bc:
                currentKeyholderLeaving = True
            else:
                error = self.visits.checkOutMember(
                    dbConnection, barcode)
        if currentKeyholderLeaving:
            return current_keyholder_bc
        return False
    # This returns whether the current keyholder would be leaving

    def bulkUpdate(self, dbConnection, check_ins, check_outs):
        current_keyholder_bc = self.checkin(dbConnection, check_ins)
        return self.checkout(dbConnection, current_keyholder_bc, check_outs)
