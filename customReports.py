import sqlite3
import os


class CustomReports:
    def __init__(self, database):
        self.database = database

    def migrate(self, dbConnection, db_schema_version):
        if db_schema_version < 7:
            dbConnection.execute('''CREATE TABLE reports
                                 (report_id INTEGER PRIMARY KEY,
                                 name TEXT UNIQUE,
                                 sql_text TEXT,
                                 parameters TEXT,
                                 active INTEGER default 1)''')

    def injectData(self, dbConnection, data):
        for datum in data:
            dbConnection.execute(
                "INSERT INTO reports VALUES (?,?,?,'',1)",
                (datum["report_id"], datum["name"], datum["sql_text"]))

    def readOnlyConnect(self):
        return sqlite3.connect('file:' + self.database + '?mode=ro', uri=True)

    def customSQL(self, sql):
        # open as read only
        with self.readOnlyConnect() as c:
            cur = c.cursor()
            cur.execute(sql)
            header = [i[0] for i in cur.description]
            rows = [list(i) for i in cur.fetchall()]
        return (header, rows)

    def customReport(self, report_id):
        with self.readOnlyConnect() as c:
            data = c.execute("SELECT * FROM reports WHERE (report_id=?)",
                             (report_id, )).fetchone()
            if data:
                title = data[1]
                sql = data[2]
                (header, rows) = self.customSQL(sql)

                return (title, sql, header, rows)
        return ("Couldn't find report", "", None, None)

    def saveCustomSQL(self, dbConnection, sql, name):
        try:
            dbConnection.execute("INSERT INTO reports VALUES (NULL,?,?,?,1)",
                                 (name, sql, ""))
            return ""
        except sqlite3.IntegrityError:
            return "Report already exists with that name"

    def get_report_list(self, dbConnection):
        report_list = []
        for row in dbConnection.execute(
                '''SELECT report_id, name
                                FROM reports
                                WHERE (active = ?)
                                ORDER BY name''', (1, )):
            report_list.append((row[0], row[1]))
        return report_list
