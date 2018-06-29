import csv
import datetime
import sqlite3
import os

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
   # obviously this needs to generate these stats instead of just making them up. :-)
      self.beginDate = beginDate;
      self.endDate = endDate;
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
      self.avgTime = self.totalHours / self.uniqueVisitors; 
      
      sortedList = sorted(list(self.visitors.values()), key=lambda x: x.hours, reverse=True);
    
      half = len(sortedList) // 2; 
      if len(sortedList) % 2:
         self.medianTime = sortedList[half].hours;
      else:
         self.medianTime = (sortedList[half - 1].hours + sortedList[half].hours) / 2.0 
 
      if len(sortedList) > 10:
         self.top10 = sortedList[:9];
      else:
         self.top10 = sortedList;

class Transaction(object):
  def __init__(self, barcode, name, description):
    self.time = datetime.datetime.now();
    self.barcode = barcode;
    self.name = name;
    self.description = description;

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

  def emptyBuilding(self):
     now = datetime.datetime.now()
     with sqlite3.connect(DB_STRING) as c:
        c.execute("UPDATE visits SET leave = ?, status = 'Forgot' WHERE status=='In'", (now,))

     # empty list of recent transactions when building automatically emptied
     self.recentTransactions = [];

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

  def recent(self, number):
     if len(self.recentTransactions):
        now = datetime.datetime.now()
        if now.hour == 3:   # If between 3am and 4am
           self.emptyBuilding();
     if number > len(self.recentTransactions):
        return self.recentTransactions[::-1];  # reversed
     else:
        return self.recentTransactions[-number:][::-1];
  
  def getStats(self, beginDate, endDate):
     return Statistics(beginDate, endDate);

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
