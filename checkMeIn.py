import cherrypy
from mako.lookup import TemplateLookup
import argparse
from visits import Visits
import datetime

DB_STRING = 'data/checkMeIn.db'
KEYHOLDER_BARCODE = '999901'

class CheckMeIn(object):
   def __init__(self):
      self.lookup = TemplateLookup(directories=['HTMLTemplates'],default_filters=['h'])
      self.visits =  Visits(DB_STRING, 'data/members.csv', 'TFI Barcode', 'TFI Display Name');
      self.keyholder_name = 'N/A';
      self.keyholder_barcode = KEYHOLDER_BARCODE;

   def template(self, name, **kwargs):
      return self.lookup.get_template(name).render(**kwargs);

   @cherrypy.expose
   def station(self,error=''):
      self.visits.checkBuilding(self.keyholder_barcode);
      return self.template('station.html',
                           todaysTransactions=self.visits.reports.transactionsToday(),
                           numberPresent=self.visits.reports.numberPresent(),
                           uniqueVisitorsToday=self.visits.reports.uniqueVisitorsToday(),
                           keyholder_name=self.keyholder_name,
                           keyholder=self.keyholder_barcode,
                           error=error)

   @cherrypy.expose
   def who_is_here(self):
      return self.template('who_is_here.html',now=datetime.datetime.now(), whoIsHere=self.visits.reports.whoIsHere())

   @cherrypy.expose
   def keyholder(self, barcode):
      error = ''
      barcode = barcode.strip();
      if barcode == KEYHOLDER_BARCODE:
          self.keyholder_name = 'N/A';
          self.visits.emptyBuilding(self.keyholder_barcode);
          self.keyholder_barcode = KEYHOLDER_BARCODE;
      else:
          (error, name) = self.visits.members.getName(barcode);
          if error:
              return self.template('keyholder.html', error=error);
          self.keyholder_name = name
          self.keyholder_barcode = barcode
          self.visits.addIfNotHere(self.keyholder_barcode)
      return self.station();

   @cherrypy.expose
   # later change this to be more ajaxy, but for now...
   def scanned(self, barcode):
      error = ''
# strip whitespace before or after barcode digits (occasionally a space comes before or after
      barcode = barcode.strip();
      if (barcode == KEYHOLDER_BARCODE) or (barcode == self.keyholder_barcode):
         return self.template('keyholder.html', whoIsHere=self.visits.reports.whoIsHere());
      else:
         error = self.visits.scannedMember(barcode);
      return self.station(error);

   @cherrypy.expose
   def admin(self,error=""):
      firstDate = self.visits.reports.getEarliestDate().isoformat()
      todayDate = datetime.date.today().isoformat()
      forgotDates = []
      for date in self.visits.reports.getForgottenDates():
          forgotDates.append(date.isoformat())
      return self.template('admin.html',forgotDates=forgotDates,
                            firstDate=firstDate,todayDate=todayDate,
                            error=error );

   @cherrypy.expose
   def reports(self, startDate, endDate):
      return self.template('reports.html', stats=self.visits.reports.getStats(startDate, endDate));

   @cherrypy.expose
   def customSQLReport(self, sql):
       data = self.visits.reports.customSQL(sql);
       return self.template('customSQL.html', sql=sql, data=data)

   @cherrypy.expose
   def addMember(self, display, barcode):
       error = self.visits.members.add(display, barcode);
       return self.admin(error);

   @cherrypy.expose
   def fixData(self, date):
       data = self.visits.reports.getData(date);
       return self.template('fixData.html', date=date,data=data)

   @cherrypy.expose
   def fixed(self, output):
       self.visits.fix(output);
       return self.admin();

   @cherrypy.expose
   def index(self):
      return self.who_is_here();

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description="CheckMeIn - building check in and out system")
   parser.add_argument('conf')
   args = parser.parse_args()

   cherrypy.quickstart(CheckMeIn(),'',args.conf)
