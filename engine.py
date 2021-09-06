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

SCHEMA_VERSION = 12

# This is the engine for all of the backend


class Engine(object):
    def __init__(self, dbPath, dbName):
        self.database = dbPath + dbName
        self.visits = Visits()
        self.guests = Guests()
        self.reports = Reports(self)
        self.teams = Teams()
        self.accounts = Accounts()
        self.devices = Devices()
        self.unlocks = Unlocks()
        # needs path since it will open read only
        self.customReports = CustomReports(self.database)
        self.certifications = Certifications()
        self.members = Members()

        if not os.path.exists(self.database):  # pragma: no cover
            if not os.path.exists(dbPath):
                os.mkdir(dbPath)
            with self.dbConnect() as c:
                self.migrate(c, 0)
        else:
            with self.dbConnect() as c:
                data = c.execute('PRAGMA schema_version').fetchone()
                if data[0] != SCHEMA_VERSION:  # pragma: no cover
                    self.migrate(c, data[0])

    def dbConnect(self):
        return sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)

    def migrate(self, dbConnection, db_schema_version):  # pragma: no cover
        if db_schema_version < SCHEMA_VERSION:
            self.visits.migrate(dbConnection, db_schema_version)
            self.members.migrate(dbConnection, db_schema_version)
            self.guests.migrate(dbConnection, db_schema_version)
            self.teams.migrate(dbConnection, db_schema_version)
            self.customReports.migrate(dbConnection, db_schema_version)
            self.certifications.migrate(dbConnection, db_schema_version)
            self.accounts.migrate(dbConnection, db_schema_version)
            self.devices.migrate(dbConnection, db_schema_version)
            self.unlocks.migrate(dbConnection, db_schema_version)
            dbConnection.execute(
                'PRAGMA schema_version = ' + str(SCHEMA_VERSION))
        elif db_schema_version != SCHEMA_VERSION:
            raise Exception("Unknown DB schema version" +
                            str(db_schema_version) + ": " + self.database)

    def getGuestLists(self, dbConnection):
        all_guests = self.guests.getList(dbConnection)

        building_guests = self.reports.guestsInBuilding(dbConnection)

        guests_not_here = [
            guest for guest in all_guests if guest not in building_guests]

        return (building_guests, guests_not_here)
