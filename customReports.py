import sqlite3
import os


class CustomReports:
    def __init__(self, database):
        self.database = database

    def createTable(self, dbConnection):
        self.migrate(dbConnection, 0)

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version < 7:
            dbConnection.execute('''CREATE TABLE reports
                                 (report_id INTEGER PRIMARY KEY,
                                 name TEXT UNIQUE,
                                 sql_text TEXT,
                                 parameters TEXT,
                                 active INTEGER default 1)''')

    def customSQL(self, sql):
        # open as read only
        with sqlite3.connect('file:' + self.database + '?mode=ro', uri=True) as c:
            cur = c.cursor()
            cur.execute(sql)
            header = [i[0] for i in cur.description]
            rows = [list(i) for i in cur.fetchall()]
            # append header to rows
            rows.insert(0, header)
        return rows

    def customReport(self, report_id):
        with sqlite3.connect('file:' + self.database + '?mode=ro', uri=True) as c:
            data = c.execute(
                "SELECT * FROM reports WHERE (report_id=?)", (report_id, )).fetchone()
            if data:
                cur = c.cursor()
                cur.execute(data[2])
                header = [i[0] for i in cur.description]
                rows = [list(i) for i in cur.fetchall()]
                # append header to rows
                rows.insert(0, header)
                return (data[1], data[2], rows)
        return ("Couldn't find report", None)

    def saveCustomSQL(self, dbConnection, sql, name):
        try:
            dbConnection.execute(
                "INSERT INTO reports VALUES (NULL,?,?,?,1)", (name, sql, ""))
            return ""
        except sqlite3.IntegrityError:
            return "Report already exists with that name"

    def get_report_list(self, dbConnection):
        report_list = []
        for row in dbConnection.execute('''SELECT report_id, name
                                FROM reports
                                WHERE (active = ?)
                                ORDER BY name''', (1,)):
            report_list.append((row[0], row[1]))
        return report_list


        # unit test
if __name__ == "__main__":  # pragma no cover
    DB_STRING = 'data/test.db'
    try:
        os.remove(DB_STRING)   # Start with a new one
    except IOError:
        pass  # Don't care if it didn't exist
