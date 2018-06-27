import cherrypy
from mako.lookup import TemplateLookup
import argparse
from members import Members
import datetime

class CheckMeIn(object):
   def __init__(self):
      self.lookup = TemplateLookup(directories=['HTMLTemplates'],default_filters=['h'])
      self.members = Members('data/members.csv', 'TFI Barcode', 'TFI Display Name');

   def template(self, name, **kwargs):
      return self.lookup.get_template(name).render(**kwargs);

   @cherrypy.expose
   def station(self):
      return self.template('station.html',members=self.members)

   @cherrypy.expose
   def who_is_here(self):
      return self.template('who_is_here.html',now=datetime.datetime.now(), whoIsHere=self.members.whoIsHere())
   
   @cherrypy.expose
   # later change this to be more ajaxy, but for now...
   def scanned(self, barcode):
      self.members.scanned(barcode); 
      return self.station();
       
   @cherrypy.expose
   def index(self):
      return self.station(); 

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description="CheckMeIn - building check in and out system")
   parser.add_argument('conf')
   args = parser.parse_args()
   
   cherrypy.quickstart(CheckMeIn(),'',args.conf)
