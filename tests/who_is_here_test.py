from unittest.mock import patch

import cherrypy
from cherrypy.test import helper
from cherrypy.lib.sessions import RamSession

from checkMeIn import CheckMeIn


class SimpleCPTest(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(CheckMeIn(), '/', {})

    def test_index(self):
        self.getPage("/")
        self.assertStatus('200 OK')

    def test_links(self):
        self.getPage("/links")
        self.assertStatus('200 OK')

    def test_links_full(self):
        self.getPage("/links?barcode=100091")
        self.assertStatus('200 OK')

    def test_unlock(self):
        self.getPage("/unlock?location=BFF&barcode=100091")
        self.assertStatus('303 See Other')
