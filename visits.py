import csv
import datetime
import sqlite3
import os
from collections import defaultdict
from dateutil import parser
from members import Members
from guests import Guests
from reports import Reports

class Visits(object):
  def createDB(self, filename, barcode, display):
     self.members.loadFromCSV(filename, barcode, display);
     self.guests.createTable();

     with sqlite3.connect(self.database) as c:
        c.execute('''CREATE TABLE visits
                     (start timestamp, leave timestamp, barcode text, status text)''')

  def __init__(self, database, filename, barcode, display):
     self.database = database;
     self.members = Members(self.database);
     self.guests = Guests(self.database);
     self.reports = Reports(self.database);
     if not os.path.exists(self.database):
          self.createDB(filename, barcode, display);

  def enterGuest(self, guest_id):
     now = datetime.datetime.now();
     with sqlite3.connect(self.database) as c:
         c.execute("INSERT INTO visits VALUES (?,?,?,'In')", (now, now, guest_id));

  def leaveGuest(self, guest_id):
     now = datetime.datetime.now();
     with sqlite3.connect(self.database) as c:
         c.execute("UPDATE visits SET leave = ?, status = 'Out' WHERE (barcode==?) AND (status=='In')",(now, guest_id))

  def scannedMember(self, barcode):
     now = datetime.datetime.now();
     with sqlite3.connect(self.database) as c:
         # See if it is a valid input
        data = c.execute("SELECT displayName FROM members WHERE barcode==?", (barcode,)).fetchone();
        if data is None:
           return 'Invalid barcode: ' + barcode;
        name = data[0];
        data = c.execute("SELECT * FROM visits WHERE (barcode==?) and (status=='In')", (barcode,)).fetchone();
        if data is None:
           c.execute("INSERT INTO visits VALUES (?,?,?,'In')", (now, now, barcode));
        else:
           c.execute("UPDATE visits SET leave = ?, status = 'Out' WHERE (barcode==?) AND (status=='In')",(now, barcode))
        return '';

  def emptyBuilding(self,keyholder_barcode):
     now = datetime.datetime.now()
     with sqlite3.connect(self.database) as c:
        c.execute("UPDATE visits SET leave = ?, status = 'Forgot' WHERE status=='In'", (now,))
        c.execute("UPDATE visits SET status = 'Out' WHERE barcode==? AND leave==?", (keyholder_barcode, now))

  def addIfNotHere(self, barcode):
     now = datetime.datetime.now()
     with sqlite3.connect(self.database) as c:
         c.execute('''INSERT INTO visits (START,LEAVE,BARCODE,STATUS)
                      SELECT ?,?,?,'In'
                      WHERE NOT EXISTS(
                          SELECT 1 FROM visits
                          WHERE ((barcode==?) and (status=='In')))''',
                   (now, now, barcode, barcode));
# unit test
def testOutput(testNum, test):
  result = test;
  if result:
      print("Result: ", result)
  print(testNum, visits.reports.whoIsHere());

if __name__ == "__main__":
    DB_STRING = 'data/test.db'
    try:
       os.remove(DB_STRING);   # Start with a new one
    except:
       pass; # Don't care if it didn't exist

    visits = Visits(DB_STRING, 'data/members.csv', 'TFI Barcode', 'TFI Display Name');
    testOutput(1, '');
    testOutput(2, visits.scannedMember('100091'));
    testOutput(3, visits.scannedMember('100090'));
    testOutput(4, visits.scannedMember('100090'));
    guest_id = visits.guests.add('Guest 1');
    testOutput(5, visits.enterGuest(guest_id));
    testOutput(6, visits.leaveGuest(guest_id));
    testOutput(7, visits.scannedMember('100091'));
    testOutput(8, visits.addIfNotHere('100091'));
    testOutput(9, visits.addIfNotHere('100091'));
    testOutput(10, visits.emptyBuilding('100091'));
