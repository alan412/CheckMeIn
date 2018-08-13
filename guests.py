import csv
import sqlite3
import os
from collections import namedtuple
import datetime
from enum import IntEnum


Guest = namedtuple('Guest', ['guest_id','displayName']);

class Status(IntEnum):
    inactive = 0
    active = 1

class Guests(object):
  def __init__(self, database):
     self.database = database;
     self.date = 0;
     self.num = 1;

  def createTable(self):
      with sqlite3.connect(self.database) as c:
          c.execute('''CREATE TABLE guests
                       (guest_id TEXT UNIQUE, displayName TEXT)''')

  def migrate(self, dbConnection, db_schema_version):
      if db_schema_version == 1 or db_schema_version == 2:
         dbConnection.execute('''CREATE TABLE guests
                                (guest_id TEXT UNIQUE,
                                 displayName TEXT,
                                 email TEXT,
                                 firstName TEXT,
                                 lastName TEXT,
                                 whereFound TEXT,
                                 status INTEGER default 1
                                 )''');


  def add(self, displayName, first, last, email, whereFound):
     if self.date != datetime.date.today():
         self.date = datetime.date.today();
         self.num = 1;
     else:
         self.num = self.num + 1;
     with sqlite3.connect(self.database) as c:
         while self.num < 10000:
          try:
              guest_id = self.date.strftime("%Y%m%d") + f'{self.num:04}'
              print ("attempting " + guest_id);
              # zero padded up to 9999 for each day
              c.execute("INSERT INTO guests VALUES (?,?,?,?,?,?,?)",
                   (guest_id, displayName, email, first, last, whereFound, Status.active));
              print ("success")
          except:
              self.num = self.num + 1
          else:
              return guest_id;
  def getName(self, guest_id):
       with sqlite3.connect(self.database) as c:
          data = c.execute("SELECT displayName FROM guests WHERE guest_id==?", (guest_id,)).fetchone();
          if data is None:
             return ('Invalid: ' + guest_id,);
          else:
             # Add code here for inactive
             return ('',data[0]);

  def getList(self):
     guestList = [];
     with sqlite3.connect(self.database) as c:
        for row in c.execute("SELECT * FROM guests WHERE status is NOT ? ORDER BY displayName",(Status.inactive,)):
            guestList.append(Guest(row[0],row[1]));
     return guestList;

# unit test
if __name__ == "__main__":
    DB_STRING = 'data/test.db';
    try:
       os.remove(DB_STRING);   # Start with a new one
    except:
       pass; # Don't care if it didn't exist
    guests = Guests(DB_STRING);
    guests.createTable();

    guests.add("Test 1");
    guests.add("Test 2");
    guests.add("Test 3");

    for g in guests.getList():
        print(g);
