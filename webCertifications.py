import cherrypy
from webBase import WebBase

class WebCertifications(WebBase):
### Certifications
    #TODO - this should be cleaned up so that the webpage doesn't need a DB connection    
    def showCertifications(self, dbConnection, message, barcodes, tools, members, certifications, show_table_header=True):
        return self.template('certifications.mako', 
                                 message=message,
                                 barcodes=None,
                                 tools=tools,
                                 members=members,
                                 dbConnection=dbConnection,
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
            barcodes = self.engine.visits.getMemberBarcodesInBuilding(dbConnection)
            tools = self.engine.certifications.getAllTools(dbConnection)
            members = self.engine.members
            certifications = self.engine.certifications.getUserList(dbConnection)
            
            return self.showCertifications(dbConnection, message, barcodes,
                                           tools, members, certifications)

    @cherrypy.expose
    def certification_list_tools(self, tools):
        return self.certification_list_monitor(tools, "0", "True")

    @cherrypy.expose
    def certification_list_monitor(self, tools, start_row, show_table_header):
        message = ''
        with self.dbConnect() as dbConnection:
            barcodes = self.engine.visits.getMemberBarcodesInBuilding(dbConnection)
            start = int(start_row)
            if start <= len(barcodes):
                barcodes = barcodes[start:]
            else:
                return self.template("blank.mako")
            if show_table_header == '0' or show_table_header.upper() == 'FALSE':
                show_table_header = False

            tools = self.engine.certifications.getToolsFromList(dbConnection,tools)
            members = self.engine.members
            certifications = self.engine.certifications.getUserList(dbConnection)

            return self.showCertifications(dbConnection, message, barcodes,
                                           tools, members, certifications, show_table_header)
    @cherrypy.expose
    def all_certification_list(self):
        message = ''
        with self.dbConnect() as dbConnection:
            barcodes = None
            tools = self.engine.certifications.getAllTools(dbConnection)
            members = self.engine.members
            certifications = self.engine.certifications.getUserList(dbConnection)

            return self.showCertifications(dbConnection, message, barcodes,
                                           tools, members, certifications)