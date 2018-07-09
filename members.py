import csv
import datetime
import sqlite3
import os
from dateutil import parser

DB_STRING = "data/checkMeIn.db"

class Person(object):
  def __init__(self, name, start, leave):
    self.name = name;
    self.hours = 0.0;
    self.addVisit(start, leave);
  def addVisit(self, start, leave):
    dTime = leave - start;
    self.hours += dTime.seconds / (60 * 60);  # to convert from seconds to hours

class Statistics(object):
  def __init__(self, beginDate, endDate):
      self.beginDate = beginDate.date();
      self.endDate = endDate.date();
      self.visitors = {};

      with sqlite3.connect(DB_STRING,detect_types=sqlite3.PARSE_DECLTYPES) as c:
        for row in c.execute(
'''
SELECT start, leave, displayName, members.barcode
FROM visits
INNER JOIN members ON members.barcode = visits.barcode
WHERE (start BETWEEN ? AND ?)
''', (beginDate, endDate)):
           try:
             self.visitors[row[3]].addVisit(row[0],row[1]);
           except:
             self.visitors[row[3]] = Person(row[2], row[0], row[1]);

      self.totalHours = 0.0;

      for bar, person in self.visitors.items():
          self.totalHours += person.hours;

      self.uniqueVisitors = len(self.visitors);
      if self.uniqueVisitors == 0:
        self.avgTime = 0;
        self.medianTime = 0;
        self.top = [];
      else:
         self.avgTime = self.totalHours / self.uniqueVisitors;

         self.sortedList = sorted(list(self.visitors.values()), key=lambda x: x.hours, reverse=True);

         half = len(self.sortedList) // 2;
         if len(self.sortedList) % 2:
            self.medianTime = self.sortedList[half].hours;
         else:
            self.medianTime = (self.sortedList[half - 1].hours + self.sortedList[half].hours) / 2.0

         if len(self.sortedList) > 10:
            self.top10 = self.sortedList[:9];
         else:
            self.top10 = self.sortedList;

class Transaction(object):
  def __init__(self, barcode, name, description):
    self.time = datetime.datetime.now();
    self.barcode = barcode;
    self.name = name;
    self.description = description;

class Datum(object):
    def __init__(self, rowid, start, leave, name, status):
        self.start = start
        self.leave = leave
        self.name = name
        self.status = status
        self.rowid = rowid

class Members(object):
  def createDB(self, filename, barcode, display):
     with sqlite3.connect(DB_STRING) as c:
        c.execute('''CREATE TABLE members
                     (barcode text, displayName text)''')
        c.execute('''CREATE TABLE visits
                     (start timestamp, leave timestamp, barcode text, status text)''')
        with open(filename, newline='') as csvfile:
           reader = csv.DictReader(csvfile)
           for row in reader:
              c.execute("INSERT INTO members VALUES (?,?)", (row[barcode], row[display]));
  def __init__(self, filename, barcode, display):
     self.recentTransactions = [];
     if not os.path.exists('data/checkMeIn.db'):
          self.createDB(filename, barcode, display);

  def scanned(self, barcode):
     now = datetime.datetime.now();
     with sqlite3.connect(DB_STRING) as c:
        data = c.execute("SELECT displayName FROM members WHERE barcode==?", (barcode,)).fetchone();
        if data is None:
           return 'Invalid barcode: ' + barcode;
        name = data[0];
        data = c.execute("SELECT * FROM visits WHERE (barcode==?) and (status=='In')", (barcode,)).fetchone();
        if data is None:
           c.execute("INSERT INTO visits VALUES (?,?,?,'In')", (now, now, barcode));
           self.recentTransactions.append(Transaction(barcode, name, "In"))    # Obviously needs to be changed
        else:
           c.execute("UPDATE visits SET leave = ?, status = 'Out' WHERE (barcode==?) AND (status=='In')",(now, barcode))
           self.recentTransactions.append(Transaction(barcode, name, "Out"))
        return '';

  def getName(self, barcode):
     with sqlite3.connect(DB_STRING) as c:
        data = c.execute("SELECT displayName FROM members WHERE barcode==?", (barcode,)).fetchone();
        if data is None:
           return 'Invalid: ' + barcode;
        else:
           return data[0];

  def emptyBuilding(self,keyholder_barcode):
     now = datetime.datetime.now()
     with sqlite3.connect(DB_STRING) as c:
        print("barcode:", keyholder_barcode)
        c.execute("UPDATE visits SET leave = ?, status = 'Forgot' WHERE status=='In'", (now,))
        c.execute("UPDATE visits SET status = 'Out' WHERE barcode==? AND leave==?", (keyholder_barcode, now))

     # empty list of recent transactions when building automatically emptied
     self.recentTransactions = [];

  def addIfNotHere(self, barcode, name):
     now = datetime.datetime.now()
     with sqlite3.connect(DB_STRING) as c:
         data = c.execute("SELECT * FROM visits WHERE (barcode==?) and (status=='In')", (barcode,)).fetchone();
         if data is None:
             c.execute("INSERT INTO visits VALUES (?,?,?,'In')", (now, now, barcode));
             self.recentTransactions.append(Transaction(barcode, name, "In"))    # Obviously needs to be changed

  def whoIsHere(self):
     listPresent = [];
     with sqlite3.connect(DB_STRING,detect_types=sqlite3.PARSE_DECLTYPES) as c:
        for row in c.execute("SELECT displayName,start FROM visits INNER JOIN members ON members.barcode = visits.barcode WHERE status=='In' ORDER BY displayName"):
          listPresent.append(row[0] + ' - ( ' + row[1].strftime("%I:%M %p")  +' )');
     return listPresent

  def uniqueVisitorsToday(self):
    now = datetime.datetime.now()
    startDate = now.replace(hour=0,minute=0,second=0,microsecond=0);
    endDate = now.replace(hour=23,minute=59,second=59,microsecond=999999);
    return self.uniqueVisitors(startDate, endDate);

  def uniqueVisitors(self, startDate, endDate):
     with sqlite3.connect(DB_STRING) as c:
        numUniqueVisitors = c.execute("SELECT COUNT(DISTINCT barcode) FROM visits WHERE (start BETWEEN ? AND ?)", (startDate, endDate)).fetchone()[0]
     return numUniqueVisitors

  def recent(self, number, keyholder):
     if len(self.recentTransactions):
        now = datetime.datetime.now()
        if now.hour == 3:   # If between 3am and 4am
           self.emptyBuilding(keyholder);
        elif ((now.day > self.recentTransactions[-1].time.day) and
             (now.hour >= 3)):
           self.emptyBuilding(keyholder);

     if number > len(self.recentTransactions):
        return self.recentTransactions[::-1];  # reversed
     else:
        return self.recentTransactions[-number:][::-1];

  def getStats(self, beginDateStr, endDateStr):
    startDate = datetime.datetime(int(beginDateStr[0:4]),int(beginDateStr[5:7]),int(beginDateStr[8:10])).replace(
                    hour=0,minute=0,second=0,microsecond=0);
    endDate = datetime.datetime(int(endDateStr[0:4]),int(endDateStr[5:7]),int(endDateStr[8:10])).replace(
                    hour=23,minute=59,second=59,microsecond=999999);

    return Statistics(startDate, endDate);

  def getForgottenDates(self):
      dates = [];
      with sqlite3.connect(DB_STRING,detect_types=sqlite3.PARSE_DECLTYPES) as c:
          for row in c.execute("SELECT start FROM visits WHERE status=='Forgot'"):
              day = row[0].date();
              if day not in dates:
                  dates.append(day)
      return dates;
  def getEarliestDate(self):
      return datetime.date(2018, 6,25);  # this should get from database, but for now....

  def getData(self, dateStr):
    data = [];
    date = datetime.datetime(int(dateStr[0:4]),int(dateStr[5:7]),int(dateStr[8:10]))
    startDate = date.replace(hour=0,minute=0,second=0,microsecond=0);
    endDate = date.replace(hour=23,minute=59,second=59,microsecond=999999);

    with sqlite3.connect(DB_STRING,detect_types=sqlite3.PARSE_DECLTYPES) as c:
        for row in c.execute('''SELECT displayName,start,leave,status,visits.rowid
        FROM visits
        INNER JOIN members ON members.barcode = visits.barcode
        WHERE (start BETWEEN ? AND ?) ORDER BY start''', (startDate, endDate)):
           data.append(Datum(start=row[1],leave=row[2],name=row[0],status=row[3],rowid=row[4]));
    return data;
  def fix(self, fixData):
    entries = fixData.split(',')

    with sqlite3.connect(DB_STRING,detect_types=sqlite3.PARSE_DECLTYPES) as c:
       for entry in entries:
           tokens = entry.split('!')
           print(tokens)
           if len(tokens) == 3:
               rowID = tokens[0];
               newStart = parser.parse(tokens[1]);
               newLeave = parser.parse(tokens[2]);

               # if crossed over midnight....
               if(newLeave < newStart):
                  newLeave += datetime.timedelta(days=1)

               c.execute('''UPDATE visits SET start = ?, leave = ?, status = 'Out'
                            WHERE (visits.rowid==?)''',(newStart, newLeave, rowID))


# unit test
if __name__ == "__main__":
    members = Members('data/members.csv', 'TFI Barcode', 'TFI Display Name');
    print('1',members.whoIsHere());
    members.scanned('100091');
    print('2',members.whoIsHere());
    members.scanned('100090');
    print('3',members.whoIsHere());
    members.scanned('100090');
    print('4', members.whoIsHere());
    members.scanned('100091');
    print('5', members.whoIsHere());
    transactions =  members.recent(9);
    for trans in transactions:
       print(trans.time, ' : ', trans.name, ' - ', trans.description);

    members.scanned('100090');   # check in
    print('6', members.whoIsHere());
    members.emptyBuilding();
    print('7', members.whoIsHere());

    transactions =  members.recent(9);
    for trans in transactions:
       print(trans.time, ' : ', trans.name, ' - ', trans.description);
