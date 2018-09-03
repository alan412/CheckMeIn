from unittest.mock import patch

import cherrypy
from cherrypy.test import helper
from cherrypy.lib.sessions import RamSession

from checkMeIn import CheckMeIn


class SimpleCPTest(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(CheckMeIn(), '/', {})

    def test_station(self):
        self.getPage("/station/")
        self.assertStatus('200 OK')
    def test_scanned_success(self):
        self.getPage("/scanned?barcode=100090")
        self.assertStatus('200 OK')
    def test_scanned_keyholder_from_station(self):
        self.getPage("/scanned?barcode=999901")
        self.assertStatus('200 OK')
    def test_scanned_keyholder_from_keyholder(self):
        self.getPage("/keyholder?barcode=999901")
        self.assertStatus('200 OK')
    def test_scanned_from_keyholder(self):
        self.getPage("/keyholder?barcode=100091")
        self.assertStatus('200 OK')
    def test_scanned_failure(self):
        self.getPage("/scanned?barcode=fail")
        self.assertStatus('200 OK')
