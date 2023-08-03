import cherrypy
from webBase import WebBase


class WebCertifications(WebBase):
    # Certifications
    def showCertifications(self, message, tools, certifications, show_table_header=True, show_left_names=True, show_right_names=True):
        return self.template('certifications.mako',
                             message=message,
                             tools=tools,
                             show_table_header=show_table_header,
                             show_left_names=show_left_names,
                             show_right_names=show_right_names,
                             certifications=certifications)

    @cherrypy.expose
    def certify(self, all=False):
        certifier_id = self.getBarcode("/certifications/certify")
        message = ''
        with self.dbConnect() as dbConnection:
            members = self.engine.members.getActive(
                dbConnection) if all else self.engine.visits.getMembersInBuilding(dbConnection)

            return self.template('certify.mako', message=message,
                                 certifier=self.engine.members.getName(dbConnection,
                                                                       certifier_id)[1],
                                 certifier_id=certifier_id,
                                 members_in_building=members,
                                 tools=self.engine.certifications.getListCertifyTools(dbConnection, certifier_id))

    @cherrypy.expose
    def addCertification(self, member_id, tool_id, level):
        certifier_id = self.getBarcode("/certifications/certify")
        # We don't check here for valid tool since someone is forging HTML to put an invalid one
        # and we'll catch it with the email out...\
        with self.dbConnect() as dbConnection:
            self.engine.certifications.addNewCertification(dbConnection,
                                                           member_id, tool_id, level, certifier_id)
        with self.dbConnect() as dbConnection:  # separate out committing from getting
            memberName = self.engine.members.getName(
                dbConnection, member_id)[1]
            certifierName = self.engine.members.getName(
                dbConnection, certifier_id)[1]
            level = self.engine.certifications.getLevelName(level)
            tool = self.engine.certifications.getToolName(
                dbConnection, tool_id)

            self.engine.certifications.emailCertifiers(
                memberName, tool, level, certifierName)

        return self.template('congrats.mako', message='',
                             certifier_id=certifier_id,
                             memberName=memberName,
                             level=level,
                             tool=tool)

    @cherrypy.expose
    def index(self):
        message = ''
        with self.dbConnect() as dbConnection:
            tools = self.engine.certifications.getAllTools(dbConnection)
            certifications = self.engine.certifications.getInBuildingUserList(
                dbConnection)

            return self.showCertifications(message, tools, certifications)

    @cherrypy.expose
    def team(self, team_id):
        message = ''
        with self.dbConnect() as dbConnection:
            message = 'Certifications for team: ' + \
                self.engine.teams.teamNameFromId(dbConnection, team_id)
            tools = self.engine.certifications.getAllTools(dbConnection)
            certifications = self.engine.certifications.getTeamUserList(
                dbConnection, team_id)

            return self.showCertifications(message, tools, certifications)

    @cherrypy.expose
    def user(self, barcode):
        message = ''
        with self.dbConnect() as dbConnection:
            message = 'Certifications for Individual'
            tools = self.engine.certifications.getAllTools(dbConnection)
            certifications = self.engine.certifications.getUserList(
                dbConnection, user_id=barcode)

            return self.showCertifications(message, tools, certifications)

    def getBoolean(self, term):
        if term == '0' or term.upper() == 'FALSE':
            return False
        return True

    @cherrypy.expose
    def monitor(self, tools, start_row=0, show_left_names="True", show_right_names="True", show_table_header="True"):
        message = ''
        with self.dbConnect() as dbConnection:
            certifications = self.engine.certifications.getInBuildingUserList(
                dbConnection)
            start = int(start_row)
            if start <= len(certifications):
                # This depends on python 3.6 or higher for the dictionary to be ordered by insertion order
                listCertKeys = list(certifications.keys())[start:]
                subsetCerts = {}
                for cert in listCertKeys:
                    subsetCerts[cert] = certifications[cert]
                certifications = subsetCerts
            else:
                return self.template("blank.mako")

            show_table_header = self.getBoolean(show_table_header)
            show_left_names = self.getBoolean(show_left_names)
            show_right_names = self.getBoolean(show_right_names)

            tools = self.engine.certifications.getToolsFromList(
                dbConnection, tools)

            return self.showCertifications(message, tools, certifications, show_table_header, show_left_names, show_right_names)

    @cherrypy.expose
    def all(self):
        message = ''
        with self.dbConnect() as dbConnection:
            tools = self.engine.certifications.getAllTools(dbConnection)
            certifications = self.engine.certifications.getAllUserList(
                dbConnection)

            return self.showCertifications(message, tools, certifications)
