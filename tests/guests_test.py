import cherrypy
from cherrypy.test import helper

from checkMeIn import CheckMeIn


class SimpleCPTest(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(CheckMeIn(), '/', {})

    def test_guests(self):
        self.getPage("/guests/")
        self.assertStatus('200 OK')

    def test_addGuest(self):
        self.getPage(
            "/addGuest?first=Fred&last=Guest&email=&reason=Tour&other_reason=")
        self.assertStatus('200 OK')

    def test_addGuest_blankName(self):
        self.getPage(
            "/addGuest?first=&last=Guest&email=&reason=Tour&other_reason=")
        self.assertStatus('200 OK')

    def test_addGuest_otherReason(self):
        self.getPage(
            "/addGuest?first=First&last=Guest&email=&reason=&other_reason=Random")
        self.assertStatus('200 OK')

    def test_returnGuest(self):
        self.getPage("/returnGuest?guest_id=201808180002")
        self.assertStatus('200 OK')

    def test_returnGuestError(self):
        self.getPage("/returnGuest?guest_id=error")
        self.assertStatus('200 OK')

    def test_leaveGuest(self):
        self.getPage("/leaveGuest?guest_id=201809030001")
        self.assertStatus('200 OK')

    def test_leaveGuestError(self):
        self.getPage("/leaveGuest?guest_id=error")
        self.assertStatus('200 OK')
