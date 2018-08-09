import csv
import sqlite3
import os
from collections import namedtuple
import datetime

Guest = namedtuple('Guest', ['guest_id','displayName']);

class Guests(object):
  def __init__(self, database):
     self.database = database;
     self.date = 0;
     self.num = 1;

  def createTable(self):
      with sqlite3.connect(self.database) as c:
          c.execute('''CREATE TABLE guests
                       (guest_id TEXT UNIQUE, displayName TEXT)''')

  def add(self, displayName):
     if self.date != datetime.date.today():
         self.date = datetime.date.today();
         self.num = 1;
     else:
         self.num = self.num + 1;
     with sqlite3.connect(self.database) as c:
         while self.num < 10000:
          try:
              guest_id = self.date.strftime("%Y%m%d") + f'{self.num:04}'
              # zero padded up to 9999 for each day
              c.execute("INSERT INTO guests VALUES (?,?)",
                   (guest_id, displayName));
          except:
              self.num = self.num + 1
          else:
              break;

  def getGuests(self):
     guestList = [];
     with sqlite3.connect(self.database) as c:
        for row in c.execute("SELECT * FROM guests"):
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

    for g in guests.getGuests():
        print(g);
