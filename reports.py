from guests import Guest
import matplotlib.pyplot as plt
import sqlite3
import datetime
from io import BytesIO
from collections import defaultdict
from collections import namedtuple
import matplotlib
# The pylint disable is because it doesn't like the use before other imports
matplotlib.use('Agg')   # pylint: disable=C0413


Transaction = namedtuple('Transaction', ['name', 'time', 'description'])
Datum = namedtuple('Datum', ['rowid', 'start', 'leave', 'name', 'status'])

VisitorsAtTime = namedtuple('VisitorsAtTime', ['startTime', 'numVisitors'])

PersonInBuilding = namedtuple(
    'PersonInBuilding', ['displayName', 'barcode', 'start'])


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


class Person(object):
    def __init__(self, name, start, leave):
        self.name = name
        self.hours = 0.0
        self.date = defaultdict(float)
        self.addVisit(start, leave)

    def addVisit(self, start, leave):
        dTime = leave - start
        # convert from seconds to hours
        hours = (float)(dTime.seconds / (60.0 * 60.0))
        self.hours += hours
        self.date[start.date()] += hours


class Visit(object):
    def __init__(self, start, leave):
        self.start = start
        self.leave = leave

    def inRange(self, startTime, endTime):
        # if start time is in between
        if(self.start <= endTime) and (self.start >= startTime):
            return True
        # OR if end time is in between
        if(self.leave <= endTime) and (self.leave >= startTime):
            return True
        # OR if start time is before AND end time is after
        if(self.start <= startTime) and (self.leave >= endTime):
            return True
        # else False
        return False


class BuildingUsage(object):
    def __init__(self):
        self.visits = []

    def addVisit(self, start, leave):
        self.visits.append(Visit(start, leave))

    def inRange(self, start, leave):
        numVisitors = 0
        for visit in self.visits:
            if visit.inRange(start, leave):
                numVisitors += 1
        return numVisitors


class Statistics(object):
    def __init__(self, dbConnection, beginDate, endDate):
        self.beginDate = beginDate.date()
        self.endDate = endDate.date()
        self.visitors = {}
        self.buildingUsage = BuildingUsage()

        for row in dbConnection.execute(
                '''SELECT start, leave, displayName, visits.barcode
   FROM visits
   INNER JOIN members ON members.barcode = visits.barcode
   WHERE (start BETWEEN ? AND ?)
   UNION
   SELECT start, leave, displayName, visits.barcode
   FROM visits
   INNER JOIN guests ON guests.guest_id = visits.barcode
   WHERE (start BETWEEN ? AND ?)''', (beginDate, endDate, beginDate, endDate)):
            try:
                self.visitors[row[3]].addVisit(row[0], row[1])
            except KeyError:
                self.visitors[row[3]] = Person(row[2], row[0], row[1])
            self.buildingUsage.addVisit(row[0], row[1])
        self.totalHours = 0.0

        for _, person in self.visitors.items():
            self.totalHours += person.hours

        self.uniqueVisitors = len(self.visitors)
        if self.uniqueVisitors == 0:
            self.avgTime = 0
            self.medianTime = 0
            self.sortedList = []
        else:
            self.avgTime = self.totalHours / self.uniqueVisitors

            self.sortedList = sorted(
                list(self.visitors.values()), key=lambda x: x.hours, reverse=True)

            half = len(self.sortedList) // 2
            if len(self.sortedList) % 2:
                self.medianTime = self.sortedList[half].hours
            else:
                self.medianTime = (
                    self.sortedList[half - 1].hours + self.sortedList[half].hours) / 2.0

    def getBuildingUsage(self):
        dataPoints = []
        for day in daterange(self.beginDate, self.endDate + datetime.timedelta(days=1)):
            beginTimePeriod = datetime.datetime.combine(
                day, datetime.datetime.min.time())
            # Care about 8am-10pm
            for startHour in range(8, 22):
                beginTimePeriod = beginTimePeriod.replace(
                    hour=startHour, minute=0, second=0, microsecond=0)
                endTimePeriod = beginTimePeriod + \
                    datetime.timedelta(seconds=60*60)
                dataPoints.append(VisitorsAtTime(
                    beginTimePeriod, self.buildingUsage.inRange(beginTimePeriod, endTimePeriod)))
        return dataPoints

    def getBuildingUsageGraph(self):
        dates = []
        values = []
        fig = plt.figure()
        for point in self.getBuildingUsage():
            dates.append(matplotlib.dates.date2num(point.startTime))
            values.append(point.numVisitors)

        fig, ax = plt.subplots()
        plt.plot_date(x=dates, y=values, fmt="r-")
        title_text = "Building usage\n" + \
            self.beginDate.strftime("%b %e, %G")
        if self.beginDate != self.endDate:
            title_text += " - " + self.endDate.strftime("%b %e, %G")

        plt.title(title_text, fontsize=14)
        plt.ylabel("Number of visitors")
        plt.grid(True)
        ax.xaxis.set_tick_params(rotation=30, labelsize=5)
        figData = BytesIO()
        fig.set_size_inches(8, 6)
        fig.savefig(figData, format='png', dpi=100)
        return figData.getvalue()


class Reports(object):
    def __init__(self, engine):
        self.engine = engine

    def whoIsHere(self, dbConnection):
        keyholders = self.engine.accounts.getKeyholderBarcodes(dbConnection)
        listPresent = []
        for row in dbConnection.execute('''SELECT displayName, start, visits.barcode
           FROM visits
           INNER JOIN members ON members.barcode = visits.barcode
           WHERE visits.status=='In'
           UNION
           SELECT displayName, start, visits.barcode
           FROM visits
           INNER JOIN guests ON guests.guest_id = visits.barcode
           WHERE visits.status=='In' ORDER BY displayName'''):
            displayName = row[0]
            if(row[2] in keyholders):
                displayName = displayName + "(Keyholder)"
            listPresent.append(
                PersonInBuilding(displayName=displayName,
                                 barcode=row[2], start=row[1]))
        return listPresent

    def whichTeamMembersHere(self, dbConnection, team_id, startTime, endTime):
        listPresent = []
        for row in dbConnection.execute('''SELECT displayName
           FROM visits
           INNER JOIN members ON members.barcode = visits.barcode
           INNER JOIN team_members ON team_members.barcode = visits.barcode
           WHERE (visits.start <= ?) AND (visits.leave >= ?) AND team_members.team_id = ?
           ORDER BY displayName ASC''', (endTime, startTime, team_id)):
            listPresent.append(row[0])
        return listPresent

    def guestsInBuilding(self, dbConnection):
        listPresent = []
        for row in dbConnection.execute('''SELECT displayName, start, guests.guest_id
           FROM visits
           INNER JOIN guests ON guests.guest_id = visits.barcode
           WHERE visits.status=='In' ORDER BY displayName'''):
            listPresent.append(Guest(row[2], row[0]))
        return listPresent

    def numberPresent(self, dbConnection):
        (numPeople, ) = dbConnection.execute(
            "SELECT count(*) FROM visits WHERE status == 'In'").fetchone()
        return numPeople

    def transactions(self, dbConnection, startDate, endDate):
        keyholders = self.engine.accounts.getKeyholderBarcodes(dbConnection)

        listTransactions = []
        for row in dbConnection.execute('''SELECT displayName, start, leave, visits.status, visits.barcode
           FROM visits
           INNER JOIN members ON members.barcode = visits.barcode
           WHERE (start BETWEEN ? and ?)
           UNION
           SELECT displayName, start, leave, visits.status, visits.barcode
           FROM visits
           INNER JOIN guests ON guests.guest_id = visits.barcode
           WHERE (start BETWEEN ? and ?)
           ORDER BY start''', (startDate, endDate, startDate, endDate)):
            displayName = row[0]
            if(row[4] in keyholders):
                displayName = displayName + "(Keyholder)"

            listTransactions.append(Transaction(displayName, row[1], 'In'))
            if row[3] != 'In':
                listTransactions.append(
                    Transaction(displayName, row[2], row[3]))

        return sorted(listTransactions, key=lambda x: x[1], reverse=True)

    def transactionsToday(self, dbConnection):
        now = datetime.datetime.now()
        startDate = now.replace(hour=0, minute=0, second=0, microsecond=0)
        endDate = now.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        return self.transactions(dbConnection, startDate, endDate)

    def uniqueVisitors(self, dbConnection, startDate, endDate):
        numUniqueVisitors = dbConnection.execute(
            "SELECT COUNT(DISTINCT barcode) FROM visits WHERE (start BETWEEN ? AND ?)",
            (startDate, endDate)).fetchone()[0]
        return numUniqueVisitors

    def uniqueVisitorsToday(self, dbConnection):
        now = datetime.datetime.now()
        startDate = now.replace(hour=0, minute=0, second=0, microsecond=0)
        endDate = now.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        return self.uniqueVisitors(dbConnection, startDate, endDate)

    def getStats(self, dbConnection, beginDateStr, endDateStr):
        startDate = datetime.datetime(int(beginDateStr[0:4]),
                                      int(beginDateStr[5:7]), int(beginDateStr[8:10])).replace(
            hour=0, minute=0, second=0, microsecond=0)
        endDate = datetime.datetime(int(endDateStr[0:4]),
                                    int(endDateStr[5:7]), int(endDateStr[8:10])).replace(
            hour=23, minute=59, second=59, microsecond=999999)

        return Statistics(dbConnection, startDate, endDate)

    def getEarliestDate(self, dbConnection):
        data = dbConnection.execute(
            "SELECT start FROM visits ORDER BY start ASC LIMIT 1").fetchone()
        return data[0]

    def getForgottenDates(self, dbConnection):
        dates = []
        for row in dbConnection.execute("SELECT start FROM visits WHERE status=='Forgot'"):
            day = row[0].date()
            if day not in dates:
                dates.append(day)
        return dates

    def getData(self, dbConnection, dateStr):
        data = []
        date = datetime.datetime(int(dateStr[0:4]), int(
            dateStr[5:7]), int(dateStr[8:10]))
        startDate = date.replace(hour=0, minute=0, second=0, microsecond=0)
        endDate = date.replace(
            hour=23, minute=59, second=59, microsecond=999999)

        for row in dbConnection.execute('''SELECT displayName, start, leave, visits.status, visits.rowid
           FROM visits
           INNER JOIN members ON members.barcode = visits.barcode
           WHERE (start BETWEEN ? and ?)
           UNION
           SELECT displayName, start, leave, visits.status, visits.rowid
           FROM visits
           INNER JOIN guests ON guests.guest_id = visits.barcode
           WHERE (start BETWEEN ? and ?)
           ORDER BY start''', (startDate, endDate, startDate, endDate)):
            data.append(
                Datum(start=row[1], leave=row[2], name=row[0], status=row[3], rowid=row[4]))
        return data
