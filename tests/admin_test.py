
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
    def test_bulkadd(self):
        filecontents = '''"First Name","Last Name","TFI Barcode for Button","TFI Barcode AUTO","TFI Barcode AUTONUM","TFI Display Name for Button","Membership End Date"\n
"Sasha","Mellendorf","101337","","101337","Sasha M","6/30/2020"\n
"Linda","Whipker","100063","","101387","","6/30/2020"\n
"Test","User","","","101387","",""\n
'''
        filesize = len(filecontents)
        h = [('Content-type', 'multipart/form-data; boundary=x'),
             ('Content-Length', str(108 + filesize))]
        b = ('--x\n'
             'Content-Disposition: form-data; name="csvfile"; '
             'filename="bulkadd.csv"\r\n'
             'Content-Type: text/plain\r\n'
             '\r\n')
        b += filecontents + '\n--x--\n'

        self.getPage('/admin/bulkAddMembers', h, 'POST', b)
        self.assertStatus('200 OK')
