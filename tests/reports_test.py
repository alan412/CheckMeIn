import CPtest


class ReportsTest(CPtest.CPTest):
    def test_report_page(self):
        with self.patch_session():
            self.getPage("/reports/")
            self.assertStatus('200 OK')

    def test_reports(self):
        with self.patch_session():
            self.getPage(
                "/reports/standard?startDate=2018-09-03&endDate=2023-09-03")
        self.assertStatus('200 OK')

    def test_reports_nodata(self):
        with self.patch_session():
            self.getPage(
                "/reports/standard?startDate=2018-09-03&endDate=2018-09-03")
        self.assertStatus('200 OK')

    def test_sql(self):
        with self.patch_session():
            self.getPage(
                "/reports/customSQLReport?sql=SELECT+*+FROM+members%3B%0D%0A+++++"
            )
        self.assertStatus('200 OK')

    def test_bad_sql(self):
        with self.patch_session():
            self.getPage(
                "/reports/customSQLReport?sql=SELECT+FROM+members%3B%0D%0A+++++"
            )
        self.assertStatus('200 OK')

    def tests_savereport(self):
        with self.patch_session():
            self.getPage(
                "/reports/saveCustom?sql=SELECT+*+FROM+members%3B%0D%0A+++++&report_name=all_members"
            )
        self.assertStatus('200 OK')

    def tests_savereport_duplicate(self):
        with self.patch_session():
            self.getPage(
                "/reports/saveCustom?sql=SELECT+*+FROM+members%3B%0D%0A+++++&report_name=all_members"
            )
        self.assertStatus('200 OK')

    def test_customReportGood(self):
        with self.patch_session():
            self.getPage("/reports/savedCustom?report_id=1")
        self.assertStatus('200 OK')

    def test_customReportBad(self):
        with self.patch_session():
            self.getPage("/reports/savedCustom?report_id=100")
        self.assertStatus('200 OK')

    def test_buildingGraph(self):
        with self.patch_session():
            self.getPage(
                "/reports/graph?startDate=2019-12-01&endDate=2022-12-30")
        self.assertStatus('200 OK')

    def test_tracing(self):
        with self.patch_session():
            self.getPage("/reports/tracing?barcode=100091&numDays=14")
