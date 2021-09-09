import CPtest


class GuestTest(CPtest.CPTest):
    def test_guests(self):
        self.getPage("/guests/")
        self.assertStatus('200 OK')

    def test_addGuest(self):
        self.getPage(
            "/guests/addGuest?first=Fred&last=Guest&email=&reason=Tour&other_reason=&newsletter=1"
        )
        self.assertStatus('200 OK')

    def test_addGuestSecond(self):
        self.getPage(
            "/guests/addGuest?first=Anne&last=Guest&email=&reason=Tour&other_reason=&newsletter=1"
        )
        self.assertStatus('200 OK')

    def test_addGuest_blankName(self):
        self.getPage(
            "/guests/addGuest?first=&last=Guest&email=&reason=Tour&other_reason=&newsletter=1"
        )
        self.assertStatus('200 OK')

    def test_addGuest_otherReason(self):
        self.getPage(
            "/guests/addGuest?first=First&last=Guest&email=&reason=&other_reason=Random&newsletter=1"
        )
        self.assertStatus('200 OK')

    def test_returnGuest(self):
        self.getPage("/guests/returnGuest?guest_id=201910190006")
        self.assertStatus('200 OK')

    def test_returnGuestError(self):
        self.getPage("/guests/returnGuest?guest_id=error")
        self.assertStatus('200 OK')

    def test_leaveGuest(self):
        self.getPage("/guests/leaveGuest?guest_id=201910190006")
        self.assertStatus('200 OK')

    def test_leaveGuestError(self):
        self.getPage("/guests/leaveGuest?guest_id=error")
        self.assertStatus('200 OK')
