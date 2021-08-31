# This is for getting a list of everyone who has been in the building
# at the same time as someone else
import datetime


class Member(object):
    def __init__(self, barcode, displayName, email):
        self.barcode = barcode
        self.displayName = displayName
        self.email = email

    def __repr__(self):
        return f"{self.displayName} ({self.barcode})"


class Tracing(object):
    def whoElseWasHere(self, dbConnection, barcode, startTime, endTime):
        listPresent = []
        for row in dbConnection.execute('''SELECT visits.barcode, displayName, email
           FROM visits
           INNER JOIN members ON members.barcode = visits.barcode
           WHERE (visits.start <= ?) AND (visits.leave >= ?) AND (visits.barcode != ?)
           UNION
           SELECT visits.barcode, displayName, email
           FROM visits
           INNER JOIN guests ON guests.guest_id = visits.barcode
           WHERE (visits.start <= ?) AND (visits.leave >= ?) AND (visits.barcode != ?)
           ORDER BY displayName ASC''', (endTime, startTime, barcode, endTime, startTime, barcode)):
            listPresent.append(Member(row[0], row[1], row[2]))
        return listPresent

    def getDictVisits(self, dbConnection, barcode, numDays):
        timeDelta = datetime.timedelta(days=int(numDays))
        endDate = datetime.datetime.now()
        endDate.replace(
            hour=0, minute=0, second=0, microsecond=0)
        startDate = endDate - timeDelta

        dictVisits = {}
        for row in dbConnection.execute('''SELECT start, leave FROM visits
            WHERE (visits.start <= ?) AND (visits.leave >= ?) AND (barcode = ?)''',
                                        (endDate, startDate, barcode)):
            dictVisits[row[0]] = self.whoElseWasHere(
                dbConnection, barcode, row[0], row[1])

        return dictVisits
