
from unittest.mock import patch

import cherrypy
from cherrypy.test import helper
from cherrypy.lib.sessions import RamSession

from checkMeIn import CheckMeIn


class SimpleCPTest(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(CheckMeIn(), '/', {})

    def patch_session_none(self):
        sess_mock = RamSession()
        return patch('cherrypy.session', sess_mock, create=True)

    def patch_session(self):
        sess_mock = RamSession()
        sess_mock['username'] = 'alan'
        sess_mock['barcode'] = '100091'
        sess_mock['role'] = 0x30  # give me permission to EVERYTHING!!!
        return patch('cherrypy.session', sess_mock, create=True)

    def test_admin(self):
        with self.patch_session():
            self.getPage("/admin/")
            self.assertStatus('200 OK')

    def test_oops(self):
        with self.patch_session():
            self.getPage("/admin/oops")
            self.assertStatus('200 OK')

    def test_fixData(self):
        with self.patch_session():
            self.getPage("/admin/fixData?date=2018-06-28")
            self.assertStatus('200 OK')

    def test_fixedData(self):
        with self.patch_session():
            self.getPage(
                "/admin/fixed?output=3%212018-06-28+2%3A25PM%212018-06-28+3%3A25PM%2C18%212018-06-28+7%3A9PM%212018-06-28+11%3A3PM%2C")
            self.assertStatus('200 OK')

    def test_fixDataNoOutput(self):
        with self.patch_session():
            self.getPage("/admin/fixed?output=")
            self.assertStatus('200 OK')

    def test_create(self):
        with self.patch_session():
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

        with self.patch_session():
            self.getPage('/admin/bulkAddMembers', h, 'POST', b)
            self.assertStatus('200 OK')

    def test_users(self):
        with self.patch_session():
            self.getPage("/admin/users")
            self.assertStatus('200 OK')

    def test_changeAccess(self):
        with self.patch_session():
            self.getPage(
                "/admin/changeAccess?barcode=10091&admin=1&keyholder=1")
            self.assertStatus('303 See Other')

    def test_notloggedIn(self):
        with self.patch_session_none():
            self.getPage("/admin/")
            self.assertStatus('303 See Other')

    # this is done at 2am
    def test_emptyBuilding(self):
        self.getPage("/admin/emptyBuilding")

    def test_addUser(self):
        with self.patch_session():
            self.getPage("/admin/addUser?user=Fred&barcode=100093")

    def test_deleteUser(self):
        with self.patch_session():
            self.getPage("/admin/deleteUser?barcode=100093")
