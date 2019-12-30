
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

    def test_reports(self):
        self.getPage("/reports?startDate=2018-09-03&endDate=2018-09-03")
        self.assertStatus('200 OK')

    def test_sql(self):
        self.getPage(
            "/customSQLReport?sql=SELECT+*+FROM+members%3B%0D%0A+++++")
        self.assertStatus('200 OK')

    def test_oops(self):
        self.getPage("/oops")
        self.assertStatus('200 OK')

    def test_fixData(self):
        self.getPage("/fixData?date=2018-06-28")
        self.assertStatus('200 OK')

    def test_fixDataOutput(self):
        self.getPage("/fixed?output=")
        self.assertStatus('200 OK')

    def test_customReportGood(self):
        self.getPage("/savedReport?report_id=1")
        self.assertStatus('200 OK')

    def test_customReportBad(self):
        self.getPage("/savedReport?report_id=100")
        self.assertStatus('200 OK')

    def test_buildingGraph(self):
        self.getPage("/reportGraph?startDate=2019-12-01&endDate=2019-12-30")
        self.assertStatus('200 OK')
