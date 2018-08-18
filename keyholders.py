import sqlite3
import os
from enum import IntEnum

class Status(IntEnum):
    inactive = 0
    active = 1

class Keyholders(object):
  def __init__(self, database):
     self.database = database;

  def createTable(self):
      with sqlite3.connect(self.database) as c:
          c.execute('''CREATE TABLE keyholders
                       (barcode TEXT PRIMARY KEY, active INTEGER default 0)''')

  def migrate(self, dbConnection, db_schema_version):
      if db_schema_version < 4:
         dbConnection.execute('''CREATE TABLE keyholders
                                 (barcode TEXT PRIMARY KEY, active INTEGER default 0)''')

  def setActiveKeyholder(self, barcode):
      with sqlite3.connect(self.database) as c:
          c.execute("UPDATE keyholders SET active = ? WHERE (active==?)",(Status.inactive, Status.active))
          if barcode:
             c.execute("REPLACE INTO keyholders (barcode, active) VALUES (?,?)", (barcode, Status.active))

  def getActiveKeyholder(self):
       with sqlite3.connect(self.database) as c:
          data = c.execute("SELECT barcode FROM keyholders WHERE active==?", (Status.active,)).fetchone();
          if data is None:
             return '';
          else:
             return data[0];

# unit test
if __name__ == "__main__":
    DB_STRING = 'data/test.db';
    try:
       os.remove(DB_STRING);   # Start with a new one
    except:
       pass; # Don't care if it didn't exist
    keyholders = Keyholders(DB_STRING)
    keyholders.createTable();

    keyholders.setActiveKeyholder('100090')
    print("Active: ", keyholders.getActiveKeyholder());

    keyholders.setActiveKeyholder('100091')
    print("Active: ", keyholders.getActiveKeyholder());

    keyholders.setActiveKeyholder('100090')
    print("Active: ", keyholders.getActiveKeyholder());

    keyholders.setActiveKeyholder('')
    print("Active: ", keyholders.getActiveKeyholder());
