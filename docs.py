class Doc:
    def __init__(self, summary, code, returns, notes):
        self.summary = summary
        self.code = code
        self.returns = returns
        self.notes = notes


def getDocumentation():
    return [
        Doc('CheckIn', '/station/checkin?barcode=<barcode>',
            returns='Returns the station webpage',
            notes=['This checks the specified barcode into the building, if already checked in then it does nothing',
                   'If you are the first keyholder checking in, it will make you the keyholder']),
        Doc('CheckOut', '/station/checkout?barcode=<barcode>',
            returns='Returns the station webpage',
            notes=['This checks the specified barcode out of the building, if already checked out then it does nothing',
                   "If you are the active keyholder and you checkout AND you are not the only one in the building then you'll"
                   "get a list of who is in the building and a chance to checkout or cancel. "
                   "(If you wait 30 seconds it will cancel on its own)"]),
        Doc('Make New Keyholder', '/station/makeKeyholder?barcode=<barcode>',
            returns='Returns the station webpage',
            notes=["This makes the given barcode the active keyholder.   If that barcode wasn't checked in, it also checks it in"]),
        Doc('Links', '/links[?barcode=<barcode>]',
            returns="Returns a webpage",
            notes=["This shows a list of links that barcode might find useful based off their role",
                   "If barcode is left off, it is a list of links for display stations"]),
        Doc('Unlock', '/unlock?location=BFF&barcode=<barcode>',
            returns="Returns the station webpage",
            notes=["This records the door was unlocked and checks the person that unlocks it in.  For use of door app ONLY"]),
        Doc('Get Keyholder list', '/admin/getKeyholderJSON',
            returns="Encrypted JSON",
            notes=["This is how the doorapp gets the updated list.  It is encrypted using Fernet (symmetric) encryption with a 32 byte key that both the doorapp and checkmeIn share.",
                   "Not useful except for the doorapp"])
    ]
