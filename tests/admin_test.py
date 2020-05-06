
from unittest.mock import patch

import cherrypy
from cherrypy.test import helper
from cherrypy.lib.sessions import RamSession

from checkMeIn import CheckMeIn


class SimpleCPTest(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(CheckMeIn(), '/', {})

    def test_admin(self):
        self.getPage("/admin/")
        self.assertStatus('200 OK')

    def test_oops(self):
        self.getPage("/admin/oops")
        self.assertStatus('200 OK')

    def test_fixData(self):
        self.getPage("/admin/fixData?date=2018-06-28")
        self.assertStatus('200 OK')

    def test_fixDataOutput(self):
        self.getPage("/admin/fixed?output=")
        self.assertStatus('200 OK')
    
    def test_create(self):
        self.getPage("/admin/createTeam?team_name=Test")
        self.assertStatus('200 OK')