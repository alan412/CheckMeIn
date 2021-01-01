
from unittest.mock import patch

import cherrypy
from cherrypy.test import helper
from cherrypy.lib.sessions import RamSession

from checkMeIn import CheckMeIn


class SimpleCPTest(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(CheckMeIn(), '/', {})

    def patch_session(self):
        sess_mock = RamSession()
        sess_mock['username'] = 'alan'
        sess_mock['barcode'] = '100091'
        sess_mock['role'] = 0xFF  # give me permission to EVERYTHING!!!
        return patch('cherrypy.session', sess_mock, create=True)

    def patch_session_none(self):
        sess_mock = RamSession()
        return patch('cherrypy.session', sess_mock, create=True)

    def patch_session_coach_alan(self):
        sess_mock = RamSession()
        sess_mock['username'] = 'alan'
        sess_mock['barcode'] = '100091'
        sess_mock['role'] = 0x04
        return patch('cherrypy.session', sess_mock, create=True)

    def patch_session_coach_abigail(self):
        sess_mock = RamSession()
        sess_mock['username'] = 'abigail'
        sess_mock['barcode'] = '100090'
        sess_mock['role'] = 0x04
        return patch('cherrypy.session', sess_mock, create=True)

    def patch_session_noncoach(self):
        sess_mock = RamSession()
        sess_mock['username'] = 'abigail'
        sess_mock['barcode'] = '100090'
        sess_mock['role'] = 0x00  # give me permission to NOTHING
        return patch('cherrypy.session', sess_mock, create=True)

    def test_blank_index(self):
        with self.patch_session():
            self.getPage("/teams/")
            self.assertStatus('303 See Other')

    def test_index(self):
        with self.patch_session():
            self.getPage("/teams/?team_id=1")
            self.assertStatus('200 OK')

    def test_index_coach_good(self):
        with self.patch_session_coach_alan():
            self.getPage("/teams/?team_id=1")
            self.assertStatus('200 OK')

    def test_index_coach_bad(self):
        with self.patch_session_coach_abigail():
            self.getPage("/teams/?team_id=1")
            self.assertStatus('303 See Other')

    def test_index_noncoach(self):
        with self.patch_session_noncoach():
            self.getPage("/teams/?team_id=1")
            self.assertStatus('303 See Other')

    def test_index_bad(self):
        with self.patch_session_none():
            self.getPage("/teams/?team_id=1")
            self.assertStatus('303 See Other')

    def test_attendance(self):
        with self.patch_session():
            self.getPage(
                "/teams/attendance?team_id=1&date=2020-12-31&startTime=18%3A00&endTime=20%3A00")

    def test_addmember(self):
        with self.patch_session():
            self.getPage("/teams/addMember?team_id=1&member=100090&type=1")
            self.assertStatus('303 See Other')

    def test_removeMember(self):
        with self.patch_session():
            self.getPage("/teams/removeMember?team_id=1&member=100090")
            self.assertStatus('303 See Other')

    def test_renameTeam(self):
        with self.patch_session():
            self.getPage("/teams/renameTeam?team_id=1&newName=Fred")
            self.assertStatus('303 See Other')

    def test_newSeason(self):
        with self.patch_session():
            self.getPage("/teams/newSeason?team_id=1&100091=2")
            self.assertStatus('303 See Other')

    def test_update(self):
        with self.patch_session():
            self.getPage("/teams/update?team_id=1&100091=in&100090=out")
            self.assertStatus('303 See Other')

    def test_certification(self):
        with self.patch_session():
            self.getPage("/teams/certifications?team_id=1")
            self.assertStatus('303 See Other')
