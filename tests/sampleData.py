import datetime


def testData():
    return{
        "visits": [
            {
                "start": datetime.datetime(year=2021, month=7, day=15, hour=11),
                "leave": datetime.datetime(year=2021, month=7, day=15, hour=13),
                "barcode": "100091",
                "status": "Out"
            },
            {
                "start": datetime.datetime.now(),
                "barcode": "100091",
                "status": "In"
            },
        ],
        "members": [{
            "barcode": "100091",
            "displayName": "Member N",
            "firstName": "Member",
            "lastName": "Name",
            "email": "fake@email.com",
            "membershipExpires": datetime.datetime(year=2022, month=7, day=30),
        }, {
            "barcode": "100032",
            "displayName": "Average J",
            "firstName": "Average",
            "lastName": "Joe",
            "email": "fake@email.com",
            "membershipExpires": datetime.datetime(year=2022, month=7, day=30)
        }],
        "accounts": [{
            "user": "admin",
            "password": "password",
            "barcode": "100091",
            "role": 0xFF
        }]}
