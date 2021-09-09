import datetime


def timeAgo(days=0, hours=0):
    return datetime.datetime.now() - datetime.timedelta(days=days, hours=hours)


def testData():
    return{
        "visits": [
            {
                "start": timeAgo(days=7, hours=1),
                "leave": timeAgo(days=7, hours=0),
                "barcode": "100091",
                "status": "Out"
            },
            {
                "start": timeAgo(days=7, hours=1),
                "leave": timeAgo(days=7, hours=0),
                "barcode": "100032",
                "status": "Out"
            },
            {
                "start": timeAgo(hours=1),
                "barcode": "100091",
                "status": "In"
            },
            {
                "start": timeAgo(hours=1),
                "barcode": "202107310001",
                "status": "In"
            },
            {
                "start": timeAgo(hours=1),
                "barcode": "100032",
                "status": "In"
            },
        ],
        "members": [{
            "barcode": "100090",
            "displayName": "Daughter N",
            "firstName": "Daughter",
            "lastName": "Name",
            "email": "fake2@email.com",
            "membershipExpires": timeAgo(days=-30),
        }, {
            "barcode": "100091",
            "displayName": "Member N",
            "firstName": "Member",
            "lastName": "Name",
            "email": "fake@email.com",
            "membershipExpires": timeAgo(days=-30),
        }, {
            "barcode": "100032",
            "displayName": "Average J",
            "firstName": "Average",
            "lastName": "Joe",
            "email": "fake@email.com",
            "membershipExpires": timeAgo(days=-30)
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
        },
            {
            "team_id": 2,
            "program_name": "TFI",
            "program_number": 100,
            "team_name": "Crazy Contraptions",
            "start_date": datetime.datetime(year=2020, month=5, day=1),
            "active": 1,
            "members": [
                {"barcode": "100091", "type": 2},
                {"barcode": "100032", "type": 0}
            ]
        },
            {
            "team_id": 3,
            "program_name": "TFI",
            "program_number": 400,
            "team_name": "Inactive team",
            "start_date": datetime.datetime(year=2020, month=5, day=1),
            "active": 0,
            "members": [
                {"barcode": "100091", "type": 2},
                {"barcode": "100032", "type": 0}
            ]
        }

        ],
        "certifications": [
            {"barcode": "100091",
             "tool_id": 1,
             "level": 30,
             "date": "",
             "certifier": "LEGACY"},
            {"barcode": "100091",
             "tool_id": 1,
             "level": 40,
             "date": timeAgo(days=8),
             "certifier": "LEGACY"},
            {"barcode": "100032",
             "tool_id": 1,
             "level": 10,
             "date": timeAgo(days=10),
             "certifier": "100091"}
        ],
        "customReports": [{
            "report_id": 1,
            "name": "fred",
            "sql_text": "SELECT * FROM members;"}
        ],
        "logEvents": [{
            "what": "Bulk Add",
            "barcode": "100091",
            "date": timeAgo(hours=1)
        }],
        "unlocks": [{
            "time": timeAgo(hours=1),
            "location": "BFF",
            "barcode": "100091"
        }],
        "guests": [{
            "guest_id": "202107310001",
            "displayName": "Random G.",
            "email": "spam@email.com",
            "firstName": "Random",
            "lastName": "Guest",
            "whereFound": "invited",
            "status": "1",
            "newsletter": 1
        }],
        "devices": [{
            "mac": "87:65:43:21",
            "name": "Phone",
            "barcode": "100091"
        }]
    }
