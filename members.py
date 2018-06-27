import csv
import datetime

class MemberList(object):
  def __init__(self, filename, barcode, display):
     self.dict = dict()
     with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
         self.dict[row[barcode]] = row[display]
  def print(self):
     for barcode, display in self.dict.items():
          print(barcode, " - ", display) 
  def findName(self,barcode):
     try:
          return self.dict[barcode]
     except:
          return 'Not Found'

class Transaction(object):
  def __init__(self, barcode, name, description):
    self.time = datetime.datetime.now();
    self.barcode = barcode;
    self.name = name;
    self.description = description;

class PresentMembers(object):
  def __init__(self):
     # at some point later read from file
     self.listPresent = [];
  def inList(self,barcode):
     return barcode in self.listPresent;
  def addToList(self, barcode):
     self.listPresent.append(barcode);
  def delFromList(self, barcode): 
     self.listPresent.remove(barcode);
  def getList(self):
     return self.listPresent;
   
class Members(object):
  def __init__(self, filename, barcode, display):
     self.memberList = MemberList(filename, barcode, display);
     self.presentMembers = PresentMembers();
     self.recentTransactions = [];
  def scanned(self, barcode):
     name = self.memberList.findName(barcode);
     if self.presentMembers.inList(barcode):
         self.recentTransactions.append(Transaction(barcode, name, "Out"));
         self.presentMembers.delFromList(barcode); 
     else:
         self.recentTransactions.append(Transaction(barcode, name, "In"));
         self.presentMembers.addToList(barcode);
  def nameFromBarcode(self, barcode):
     return self.memberList.findName(barcode);
  def whoIsHere(self):
     listPresent = [];
     for barcode in self.presentMembers.getList():
        listPresent.append(self.memberList.findName(barcode));
     return listPresent
  def recent(self, number):
     if number > len(self.recentTransactions):
        return self.recentTransactions[::-1];  # reversed
     else:
        return self.recentTransactions[-number][::-1];

# unit test
if __name__ == "__main__":         
	members = Members('data/members.csv', 'TFI Barcode', 'TFI Display Name');
	print(members.whoIsHere());
	members.scanned('100091');
	print(members.whoIsHere());
	members.scanned('100090');
	print(members.whoIsHere());
	members.scanned('100090');
	print( members.whoIsHere());
	members.scanned('100091');
	print( members.whoIsHere());
	transactions =  members.recent(9);
	for trans in transactions:
	   print(trans.time, ' : ', trans.name, ' - ', trans.description);

