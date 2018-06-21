import cherrypy
from mako.lookup import TemplateLookup
import argparse

class CheckMeIn(object):
   def __init__(self):
      self.lookup = TemplateLookup(directories=['HTMLTemplates'],default_filters=['h'])
   def template(self, name, **kwargs):
      return self.lookup.get_template(name).render(**kwargs);

   @cherrypy.expose
   def station(self):
      return self.template('station.html')
   
   @cherrypy.expose
   def index(self):
      return self.station(); 

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description="CheckMeIn - building check in and out system")
   parser.add_argument('conf')
   args = parser.parse_args()
   
   cherrypy.quickstart(CheckMeIn(),'',args.conf)
