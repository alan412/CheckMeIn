from unittest.mock import patch

import cherrypy
from cherrypy.test import helper
from cherrypy.lib.sessions import RamSession

from checkMeIn import CheckMeIn


class CPTest(helper.CPWebCase):
    @staticmethod
    def setup_server():
        testConfig = {
            'global': {
                'database.path': 'testData/',
                'database.name': 'test.db'
            }
        }

        cherrypy.config.update(testConfig)
        cmi = CheckMeIn()
        print("setup cmi")
        cherrypy.tree.mount(cmi, '/', testConfig)
        return cmi

    def ingest_data(self, data):
        cmi.engine.ingest_data(data)

    def patch_session_none(self):
        sess_mock = RamSession()
        return patch('cherrypy.session', sess_mock, create=True)

    def patch_session(self, username='alan', barcode='100091', role=0xFF):
        sess_mock = RamSession()
        sess_mock['username'] = username
        sess_mock['barcode'] = barcode
        sess_mock['role'] = role
        return patch('cherrypy.session', sess_mock, create=True)
