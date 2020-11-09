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
        self.getPage("/station/scanned?barcode=100090")
        self.assertStatus('303 See Other')

    def test_scanned_success2(self):  # if before made in, this should make out
        self.getPage("/station/scanned?barcode=100090")
        self.assertStatus('303 See Other')

    def test_checkin(self):
        self.getPage("/station/checkin?barcode=100090")
        self.assertStatus('303 See Other')

    def test_checkout(self):
        self.getPage("/station/checkout?barcode=100090")
        self.assertStatus('303 See Other')

    def test_bulkUpdate(self):
        self.getPage(
            "/station/bulkUpdate?inBarcodes=100090+100091&outBarcodes=")
        self.assertStatus('303 See Other')

    def test_bulkUpdateAllOut(self):
        self.getPage("/admin/emptyBuilding")
        self.getPage("/station/makeKeyholder?barcode=100091")
        self.getPage(
            "/station/bulkUpdate?inBarcodes=100090+100091&outBarcodes=")
        self.getPage(
            "/station/bulkUpdate?inBarcodes=&outBarcodes=100090+100091")
        self.assertStatus('303 See Other')

    def test_scanned_bogus(self):
        self.getPage("/station/scanned?barcode=000090")
        self.assertStatus('303 See Other')

    def test_scanned_keyholder_from_station(self):
        self.getPage("/station/scanned?barcode=999901")
        self.assertStatus('200 OK')

    def test_makeKeyholder(self):
        self.getPage("/station/makeKeyholder?barcode=100090")
        self.assertStatus('303 See Other')

    def test_scanned_keyholder_from_keyholder(self):
        self.getPage("/station/keyholder?barcode=999901")
        self.assertStatus('303 See Other')

    def test_scanned_from_keyholder(self):
        self.getPage("/station/keyholder?barcode=100091")
        self.assertStatus('303 See Other')

    def test_scanned_failure(self):
        self.getPage("/station/scanned?barcode=fail")
        self.assertStatus('303 See Other')
