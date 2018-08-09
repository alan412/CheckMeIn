import csv
import datetime
import sqlite3
import os
from collections import defaultdict
from dateutil import parser

class Reports(object):
  def __init__(self, database):
       self.database = database;

  def whoIsHere(self):
     listPresent = [];
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
          listPresent.append(row[0] + ' - ( ' + row[1].strftime("%I:%M %p")  +' )');
     return listPresent

# unit test
if __name__ == "__main__":
   print("To test this module, you need to use visits module")
