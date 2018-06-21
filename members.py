import csv

class Members(object):
  def __init__(self, filename, barcode, display):
     self.dict = dict()
     with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
         self.dict[row[barcode]] = row[display]
  def print(self):
     for barcode, display in self.dict.items():
          print(barcode, " - ", display) 
class Member_Present(object):
   def __init__(self, name, number, time_in):
      self.name = name
      self.number = number
      self.time_in = time_in
   def getName(self):
      return self.name
   def getTimeIn(self):
      return self.time_in
   def getNumber(self):
      return self.number


members = Members('data/members.csv', 'TFI Barcode', 'TFI Display Name');
members.print();

