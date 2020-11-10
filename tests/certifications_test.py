
from unittest.mock import patch

import cherrypy
from cherrypy.test import helper
from cherrypy.lib.sessions import RamSession

from checkMeIn import CheckMeIn


class SimpleCPTest(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(CheckMeIn(), '/', {})

    def test_certify(self):
        self.getPage(
            "/certifications/certify?certifier_id=100091")
        self.assertStatus('200 OK')

    def test_invalid_certify(self):
        self.getPage(
            "/certifications/certify?certifier_id=000091")
        self.assertStatus('200 OK')

    def test_certify_all(self):
        self.getPage(
            "/certifications/certify_all?certifier_id=100090")
        self.assertStatus('200 OK')

    def test_addCertification(self):
        self.getPage(
            "/certifications/addCertification?member_id=100090&certifier_id=100091&tool_id=1&level=1")
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
