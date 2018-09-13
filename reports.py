import sqlite3
import datetime
from io import BytesIO
from collections import defaultdict
from collections import namedtuple
import matplotlib
# The pylint disable is because it doesn't like the use before other imports
matplotlib.use('Agg')   # pylint: disable=C0413
import matplotlib.pyplot as plt

from guests import Guest


Transaction = namedtuple('Transaction', ['name', 'time', 'description'])
Datum = namedtuple('Datum', ['rowid', 'start', 'leave', 'name', 'status'])

VisitorsAtTime = namedtuple('VisitorsAtTime', ['startTime', 'numVisitors'])


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

    def getTimeForDate(self, day):
        return self.date[day]


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
    def __init__(self, database, beginDate, endDate):
        self.beginDate = beginDate.date()
        self.endDate = endDate.date()
        self.visitors = {}
        self.buildingUsage = BuildingUsage()

        with sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            for row in c.execute(
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
                except:
                    self.visitors[row[3]] = Person(row[2], row[0], row[1])
                self.buildingUsage.addVisit(row[0], row[1])
        self.totalHours = 0.0

        for _, person in self.visitors.items():
            self.totalHours += person.hours

        self.uniqueVisitors = len(self.visitors)
        if self.uniqueVisitors == 0:
            self.avgTime = 0
            self.medianTime = 0
            self.top10 = []
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

            if len(self.sortedList) > 10:
                self.top10 = self.sortedList[:9]
            else:
                self.top10 = self.sortedList

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
        plt.title("Building usage")
        plt.ylabel("Number of visitors")
        plt.grid(True)
        ax.xaxis.set_tick_params(rotation=30, labelsize=5)
        figData = BytesIO()
        fig.savefig(figData, format='png')
        return figData.getvalue()


class Reports(object):
    def __init__(self, database):
        self.database = database

    def whoIsHere(self):
        listPresent = []
        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            for row in c.execute('''SELECT displayName, start
           FROM visits
           INNER JOIN members ON members.barcode = visits.barcode
           WHERE visits.status=='In'
           UNION
           SELECT displayName, start
           FROM visits
           INNER JOIN guests ON guests.guest_id = visits.barcode
           WHERE visits.status=='In' ORDER BY displayName'''):
                listPresent.append(
                    row[0] + ' - ( ' + row[1].strftime("%I:%M %p") + ' )')
        return listPresent

    def guestsInBuilding(self):
        listPresent = []
        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            for row in c.execute('''SELECT displayName, start, guests.guest_id
           FROM visits
           INNER JOIN guests ON guests.guest_id = visits.barcode
           WHERE visits.status=='In' ORDER BY displayName'''):
                listPresent.append(Guest(row[2], row[0]))
        return listPresent

    def numberPresent(self):
        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            (numPeople, ) = c.execute(
                "SELECT count(*) FROM visits WHERE status == 'In'").fetchone()
            return numPeople

    def transactions(self, startDate, endDate):
        listTransactions = []
        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            for row in c.execute('''SELECT displayName, start, leave, visits.status
           FROM visits
           INNER JOIN members ON members.barcode = visits.barcode
           WHERE (start BETWEEN ? and ?)
           UNION
           SELECT displayName, start, leave, visits.status
           FROM visits
           INNER JOIN guests ON guests.guest_id = visits.barcode
           WHERE (start BETWEEN ? and ?)
           ORDER BY start''', (startDate, endDate, startDate, endDate)):

                listTransactions.append(Transaction(row[0], row[1], 'In'))
                if row[3] != 'In':
                    listTransactions.append(
                        Transaction(row[0], row[2], row[3]))

        return sorted(listTransactions, key=lambda x: x[1], reverse=True)

    def transactionsToday(self):
        now = datetime.datetime.now()
        startDate = now.replace(hour=0, minute=0, second=0, microsecond=0)
        endDate = now.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        return self.transactions(startDate, endDate)

    def uniqueVisitors(self, startDate, endDate):
        with sqlite3.connect(self.database) as c:
            numUniqueVisitors = c.execute(
                "SELECT COUNT(DISTINCT barcode) FROM visits WHERE (start BETWEEN ? AND ?)",
                (startDate, endDate)).fetchone()[0]
        return numUniqueVisitors

    def uniqueVisitorsToday(self):
        now = datetime.datetime.now()
        startDate = now.replace(hour=0, minute=0, second=0, microsecond=0)
        endDate = now.replace(hour=23, minute=59,
                              second=59, microsecond=999999)
        return self.uniqueVisitors(startDate, endDate)

    def getStats(self, beginDateStr, endDateStr):
        startDate = datetime.datetime(int(beginDateStr[0:4]),
                                      int(beginDateStr[5:7]), int(beginDateStr[8:10])).replace(
            hour=0, minute=0, second=0, microsecond=0)
        endDate = datetime.datetime(int(endDateStr[0:4]),
                                    int(endDateStr[5:7]), int(endDateStr[8:10])).replace(
            hour=23, minute=59, second=59, microsecond=999999)

        return Statistics(self.database, startDate, endDate)

    def getEarliestDate(self):
        # TODO: this should get from database, but for now....
        return datetime.date(2018, 6, 25)

    def getForgottenDates(self):
        dates = []
        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            for row in c.execute("SELECT start FROM visits WHERE status=='Forgot'"):
                day = row[0].date()
                if day not in dates:
                    dates.append(day)
        return dates

    def getData(self, dateStr):
        data = []
        date = datetime.datetime(int(dateStr[0:4]), int(
            dateStr[5:7]), int(dateStr[8:10]))
        startDate = date.replace(hour=0, minute=0, second=0, microsecond=0)
        endDate = date.replace(
            hour=23, minute=59, second=59, microsecond=999999)

        with sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES) as c:
            for row in c.execute('''SELECT displayName, start, leave, visits.status, visits.rowid
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

    def customSQL(self, sql):
        # open as read only
        with sqlite3.connect('file:' + self.database + '?mode=ro', uri=True) as c:
            cur = c.cursor()
            cur.execute(sql)
            header = [i[0] for i in cur.description]
            rows = [list(i) for i in cur.fetchall()]
            # append header to rows
            rows.insert(0, header)
        return rows


# unit test
if __name__ == "__main__":  # pragma no cover
    print("To test this module, you need to use visits module")
