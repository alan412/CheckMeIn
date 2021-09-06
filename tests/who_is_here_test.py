import CPtest


class WhoIsHereTest(CPtest.CPTest):
    def test_index(self):
        self.getPage("/whoishere")
        self.assertStatus('200 OK')

    def test_links(self):
        with self.patch_session():
            self.getPage("/links")
        self.assertStatus('200 OK')

    def test_links_full(self):
        with self.patch_session():
            self.getPage("/links?barcode=100091")
            self.assertStatus('200 OK')

    def test_unlock(self):
        self.getPage("/unlock?location=BFF&barcode=100091")
        self.assertStatus('303 See Other')
