import cherrypy
from mako.lookup import TemplateLookup
import argparse
from members import Members
import datetime

KEYHOLDER_BARCODE = '999901'
SHOP_STEWARD_BARCODE = '999902'

class CheckMeIn(object):
   def __init__(self):
      self.lookup = TemplateLookup(directories=['HTMLTemplates'],default_filters=['h'])
      self.members = Members('data/members.csv', 'TFI Barcode', 'TFI Display Name');
      self.keyholder_name = 'N/A';
      self.keyholder_barcode = KEYHOLDER_BARCODE;
      self.shop_steward_name = 'N/A';
      self.shop_steward_barcode = SHOP_STEWARD_BARCODE;

   def template(self, name, **kwargs):
      return self.lookup.get_template(name).render(**kwargs);

   @cherrypy.expose
   def station(self,error=''):
      return self.template('station.html',members=self.members,
                           keyholder_name=self.keyholder_name,shop_steward_name=self.shop_steward_name,
                           error=error)

   @cherrypy.expose
   def who_is_here(self):
      return self.template('who_is_here.html',now=datetime.datetime.now(), whoIsHere=self.members.whoIsHere())

   @cherrypy.expose
   def keyholder(self, barcode):
      error = ''
      barcode = barcode.strip();
      if barcode == KEYHOLDER_BARCODE:
          self.keyholder_name = 'N/A';
          self.members.emptyBuilding(self.keyholder_barcode);
          self.keyholder_barcode = KEYHOLDER_BARCODE;
          self.shop_steward_name = 'N/A'
          self.shop_steward_barcode = SHOP_STEWARD_BARCODE;
      else:
          result = self.members.getName(barcode);
          if result.startswith('Invalid'):
              return self.template('keyholder.html', error=result);
          self.keyholder_name = result
          self.keyholder_barcode = barcode
          self.members.addIfNotHere(self.keyholder_barcode, self.keyholder_name)
      return self.station();

   @cherrypy.expose
   def shop_steward(self, barcode):
      error = ''
      barcode = barcode.strip();
      if barcode == SHOP_STEWARD_BARCODE:
          self.shop_steward_name = 'N/A';
          self.shop_steward_barcode = SHOP_STEWARD_BARCODE;
      else:
          result = self.members.getName(barcode);
          if result.startswith('Invalid'):
              return self.template('shop_steward.html', error=result);
          self.shop_steward_name = result
          self.shop_steward_barcode = barcode
          self.members.addIfNotHere(self.shop_steward_barcode, self.shop_steward_name)
      return self.station();

   @cherrypy.expose
   # later change this to be more ajaxy, but for now...
   def scanned(self, barcode):
      error = ''
# strip whitespace before or after barcode digits (occasionally a space comes before or after
      barcode = barcode.strip();
      if (barcode == KEYHOLDER_BARCODE) or (barcode == self.keyholder_barcode):
         return self.template('keyholder.html');
      elif (barcode == SHOP_STEWARD_BARCODE) or (barcode == self.shop_steward_barcode):
         return self.template('shop_steward.html');
      else:
         error = self.members.scanned(barcode);
      return self.station(error);

   @cherrypy.expose
   def admin(self):
      firstDate = self.members.getEarliestDate().isoformat()
      todayDate = datetime.date.today().isoformat()
      forgotDates = []
      for date in self.members.getForgottenDates():
          forgotDates.append(date.isoformat())
      return self.template('admin.html',members=self.members,forgotDates=forgotDates,
                            firstDate=firstDate,todayDate=todayDate );

   @cherrypy.expose
   def reports(self, startDate, endDate):
      return self.template('reports.html', stats=self.members.getStats(startDate, endDate));

   @cherrypy.expose
   def fixData(self, date):
       data = self.members.getData(date);
       return self.template('fixData.html', date=date,data=data)

   @cherrypy.expose
   def fixed(self, output):
       self.members.fix(output);
       return self.admin();

   @cherrypy.expose
   def index(self):
      return self.who_is_here();

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description="CheckMeIn - building check in and out system")
   parser.add_argument('conf')
   args = parser.parse_args()

   cherrypy.quickstart(CheckMeIn(),'',args.conf)
