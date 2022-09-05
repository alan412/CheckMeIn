import CPtest


class GuestTest(CPtest.CPTest):
    def test_guests(self):
        with self.patch_session():
            self.getPage("/guests/")
        self.assertStatus('200 OK')

    def test_addGuest(self):
        with self.patch_session():
            self.getPage(
                "/guests/addGuest?first=Fred&last=Guest&email=&reason=Tour&other_reason=&newsletter=1"
            )
        self.assertStatus('200 OK')

    def test_addGuestSecond(self):
        with self.patch_session():
            self.getPage(
                "/guests/addGuest?first=Anne&last=Guest&email=&reason=Tour&other_reason=&newsletter=1"
            )
        self.assertStatus('200 OK')

    def test_addGuest_blankName(self):
        with self.patch_session():
            self.getPage(
                "/guests/addGuest?first=&last=Guest&email=&reason=Tour&other_reason=&newsletter=1"
            )
        self.assertStatus('200 OK')

    def test_addGuest_otherReason(self):
        with self.patch_session():
            self.getPage(
                "/guests/addGuest?first=First&last=Guest&email=&reason=&other_reason=Random&newsletter=1"
            )
        self.assertStatus('200 OK')

    def test_returnGuest(self):
        with self.patch_session():
            self.getPage("/guests/returnGuest?guest_id=202107310001")
        self.assertStatus('200 OK')

    def test_returnGuestError(self):
        with self.patch_session():
            self.getPage("/guests/returnGuest?guest_id=error")
        self.assertStatus('200 OK')

    def test_leaveGuestNoComments(self):
        with self.patch_session():
            self.getPage("/guests/leaveGuest?guest_id=202107310001")
        self.assertStatus('200 OK')

    def test_leaveGuestWithComments(self):
        with self.patch_session():
            self.getPage(
                "/guests/leaveGuest?guest_id=202107310001&comments=Interested%20in%20donating")
        self.assertStatus('200 OK')

    def test_leaveGuestError(self):
        with self.patch_session():
            self.getPage("/guests/leaveGuest?guest_id=error")
        self.assertStatus('200 OK')
