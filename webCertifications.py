import cherrypy
from webBase import WebBase

class WebCertifications(WebBase):
### Certifications
    def showCertifications(self, message, tools, certifications, show_table_header=True):
        return self.template('certifications.mako', 
                                 message=message,
                                 tools=tools,
                                 show_table_header=show_table_header,
                                 certifications=certifications)        

    @cherrypy.expose
    def certify(self, certifier_id, all = False):
        message = ''
        with self.dbConnect() as dbConnection:
            members = self.engine.visits.getAllMembers(dbConnection) if all else self.engine.visits.getMembersInBuilding(dbConnection)

            return self.template('certify.mako', message=message,
                                 certifier=self.engine.members.getName(dbConnection,
                                                                       certifier_id)[1],
                                 certifier_id=certifier_id,
                                 members_in_building=members,
                                 tools=self.engine.certifications.getListCertifyTools(dbConnection, certifier_id))

    @cherrypy.expose
    def certify_all(self, certifier_id):
        return self.certify(certifier_id, all = True)

    @cherrypy.expose
    def addCertification(self, member_id, certifier_id, tool_id, level):
        # We don't check here for valid tool since someone is forging HTML to put an invalid one
        # and we'll catch it with the email out...\
        with self.dbConnect() as dbConnection:
            self.engine.certifications.addNewCertification(dbConnection,
                                                       member_id, tool_id, level, certifier_id)

            return self.template('congrats.mako', message='',
                                certifier_id=certifier_id,
                                memberName=self.engine.members.getName(dbConnection, member_id)[
                                    1],
                                level=self.engine.certifications.getLevelName(
                                    level),
                                tool=self.engine.certifications.getToolName(dbConnection, tool_id))

    @cherrypy.expose
    def certification_list(self):
        message = ''
        with self.dbConnect() as dbConnection:
            tools = self.engine.certifications.getAllTools(dbConnection)
            certifications = self.engine.certifications.getInBuildingUserList(dbConnection)
            
            return self.showCertifications(message, tools, certifications)

    @cherrypy.expose
    def certification_list_tools(self, tools):
        return self.certification_list_monitor(tools, "0", "True")

    @cherrypy.expose
    def certification_list_monitor(self, tools, start_row, show_table_header):
        message = ''
        with self.dbConnect() as dbConnection:
            certifications = self.engine.certifications.getInBuildingUserList(dbConnection)
            start = int(start_row)
            if start <= len(certifications):
                ### This depends on python 3.6 or higher for the dictionary to be ordered by insertion order
                listCertKeys = list(certifications.keys())[start:]
                subsetCerts = {}
                for cert in listCertKeys:
                    subsetCerts[cert] = certifications[cert]                 
                certifications = subsetCerts
            else:
                return self.template("blank.mako")
            if show_table_header == '0' or show_table_header.upper() == 'FALSE':
                show_table_header = False

            tools = self.engine.certifications.getToolsFromList(dbConnection,tools)

            return self.showCertifications(message, tools, certifications, show_table_header)
    @cherrypy.expose
    def all_certification_list(self):
        message = ''
        with self.dbConnect() as dbConnection:
            tools = self.engine.certifications.getAllTools(dbConnection)
            certifications = self.engine.certifications.getAllUserList(dbConnection)

            return self.showCertifications(message, tools, certifications)