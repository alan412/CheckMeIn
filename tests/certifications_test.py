import CPtest


class CertificationsTest(CPtest.CPTest):
    def test_certify(self):
        with self.patch_session():
            self.getPage("/certifications/certify")
        self.assertStatus('200 OK')

    def test_invalid_certify(self):
        with self.patch_session_none():
            self.getPage("/certifications/certify")
        self.assertStatus('303 See Other')

    def test_certify_all(self):
        with self.patch_session():
            self.getPage("/certifications/certify?all=True")
        self.assertStatus('200 OK')

    def test_addCertification(self):
        with self.patch_session():
            self.getPage(
                "/certifications/addCertification?member_id=100090&tool_id=1&level=1"
            )
        self.assertStatus('200 OK')

    def test_certification_list(self):
        with self.patch_session():
            self.getPage("/certifications/")
        self.assertStatus('200 OK')

    def test_monitor_normal(self):
        with self.patch_session():
            self.getPage("/certifications/monitor?tools=1_2_3")
        self.assertStatus('200 OK')

    def test_monitor_noname(self):
        with self.patch_session():
            self.getPage(
                "/certifications/monitor?tools=1_2_3&show_left_names=False&show_right_names=False")
        self.assertStatus('200 OK')

    def test_monitor_noheader(self):
        with self.patch_session():
            self.getPage(
                "/certifications/monitor?tools=1_2_3&start_row=0&show_table_header=0"
            )
        self.assertStatus('200 OK')

    def test_monitor_blank(self):
        with self.patch_session():
            self.getPage(
                "/certifications/monitor?tools=1_2_3&start_row=100&show_table_header=0"
            )
        self.assertStatus('200 OK')

    def test_all_certification_list(self):
        with self.patch_session():
            self.getPage("/certifications/all")
        self.assertStatus('200 OK')

    def test_team_certification(self):
        with self.patch_session():
            self.getPage('/certifications/team?team_id=1')
        self.assertStatus('200 OK')

    def test_team_certification_badteam(self):
        with self.patch_session():
            self.getPage('/certifications/team?team_id=35')
        self.assertStatus('200 OK')

    def test_user_certification(self):
        with self.patch_session():
            self.getPage('/certifications/user?barcode=100091')
