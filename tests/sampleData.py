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
        }],
        "teams": [{
            "team_id": 1,
            "program_name": "TFI",
            "program_number": 100,
            "team_name": "Crazy Contraptions",
            "start_date": datetime.datetime(year=2021, month=5, day=1),
            "active": 1,
            "members": [
                {"barcode": "100091", "type": 2},
                {"barcode": "100032", "type": 0}
            ]
        }],
        "certifications": [
            {"barcode": "100091",
             "tool_id": 1,
             "level": 40,
             "date": datetime.datetime(year=2021, month=4, day=1),
             "certifier": "LEGACY"},
            {"barcode": "100032",
             "tool_id": 1,
             "level": 10,
             "date": datetime.datetime(year=2021, month=4, day=1),
             "certifier": "100091"}
        ],
        "customReports": [{
            "report_id": 1,
            "name": "fred",
            "sql_text": "SELECT+*+FROM+members % 3B"}
        ],
        "logEvents": [{
            "what": "Bulk Add",
            "barcode": "100091",
            "date": datetime.datetime.now()
        }]
    }
