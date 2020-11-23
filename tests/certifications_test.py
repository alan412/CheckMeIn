
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
        sess_mock['role'] = 0xFF  # give me permission to EVERYTHING!!!
        return patch('cherrypy.session', sess_mock, create=True)

    def test_certify(self):
        with self.patch_session():
            self.getPage(
                "/certifications/certify")
        self.assertStatus('200 OK')

    def test_invalid_certify(self):
        with self.patch_session_none():
            self.getPage(
                "/certifications/certify")
        self.assertStatus('303 See Other')

    def test_certify_all(self):
        with self.patch_session():
            self.getPage(
                "/certifications/certify?all=True")
        self.assertStatus('200 OK')

    def test_addCertification(self):
        with self.patch_session():
            self.getPage(
                "/certifications/addCertification?member_id=100090&tool_id=1&level=1")
        self.assertStatus('200 OK')

    def test_certification_list(self):
        self.getPage(
            "/certifications/")
        self.assertStatus('200 OK')

    def test_monitor_normal(self):
        self.getPage(
            "/certifications/monitor?tools=1_2_3")
        self.assertStatus('200 OK')

    def test_monitor_noheader(self):
        self.getPage(
            "/certifications/monitor?tools=1_2_3&start_row=0&show_table_header=0")
        self.assertStatus('200 OK')

    def test_monitor_blank(self):
        self.getPage(
            "/certifications/monitor?tools=1_2_3&start_row=100&show_table_header=0")
        self.assertStatus('200 OK')

    def test_all_certification_list(self):
        self.getPage(
            "/certifications/all")
        self.assertStatus('200 OK')
