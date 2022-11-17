import CPtest


class StationTest(CPtest.CPTest):
    def test_station(self):
        with self.patch_session():
            self.getPage("/station/")
            self.assertStatus('200 OK')

    def test_scanned_success(self):
        with self.patch_session():
            self.getPage("/station/scanned?barcode=100090")
            self.assertStatus('303 See Other')

    def test_scanned_success2(self):  # if before made in, this should make out
        with self.patch_session():
            self.getPage("/station/scanned?barcode=100090")
            self.assertStatus('303 See Other')

    def test_checkin(self):
        with self.patch_session():
            self.getPage("/station/checkin?barcode=100091")
            self.assertStatus('303 See Other')

    def test_checkout(self):
        with self.patch_session():
            self.getPage("/station/checkout?barcode=100090")
            self.assertStatus('303 See Other')

    def test_docs(self):
        with self.patch_session():
            self.getPage("/docs")
        self.assertStatus('200 OK')

    def test_bulkUpdate(self):
        with self.patch_session():
            self.getPage(
                "/station/bulkUpdate?inBarcodes=100090+100091&outBarcodes=")
            self.assertStatus('303 See Other')

    def test_bulkUpdateAllOut(self):
        with self.patch_session():
            self.getPage("/admin/emptyBuilding")
            self.getPage("/station/makeKeyholder?barcode=100091")
            self.getPage(
                "/station/bulkUpdate?inBarcodes=100090+100091&outBarcodes=")
            self.getPage(
                "/station/bulkUpdate?inBarcodes=&outBarcodes=100090+100091")
            self.assertStatus('303 See Other')

    def test_scanned_bogus(self):
        with self.patch_session():
            self.getPage("/station/scanned?barcode=0090")
            self.assertStatus('303 See Other')

    def test_scanned_keyholder_from_station(self):
        with self.patch_session():
            self.getPage("/station/scanned?barcode=999901")
            self.assertStatus('200 OK')

    def test_makeKeyholder(self):
        with self.patch_session():
            self.getPage("/station/makeKeyholder?barcode=100091")
            self.assertStatus('200 OK')

    def test_makeKeyholder_invalid(self):
        with self.patch_session():
            self.getPage("/station/makeKeyholder?barcode=100090")
            self.assertStatus('200 OK')

    def test_scanned_keyholder_from_keyholder(self):
        with self.patch_session():
            self.getPage("/station/keyholder?barcode=999901")
            self.assertStatus('303 See Other')

    def test_scanned_from_keyholder(self):
        with self.patch_session():
            self.getPage("/station/keyholder?barcode=100091")
            self.assertStatus('303 See Other')

    def test_scanned_failure(self):
        with self.patch_session():
            self.getPage("/station/scanned?barcode=fail")
            self.assertStatus('303 See Other')
