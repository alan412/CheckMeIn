import datetime
import sqlite3
from collections import defaultdict
from collections import namedtuple
from guests import Guest

Transaction = namedtuple('Transaction', ['name', 'time', 'description'])
Datum = namedtuple('Datum', ['rowid', 'start', 'leave', 'name', 'status'])


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


class Statistics(object):
    def __init__(self, database, beginDate, endDate):
        self.beginDate = beginDate.date()
        self.endDate = endDate.date()
        self.visitors = {}

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
