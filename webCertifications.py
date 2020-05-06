import cherrypy
from webBase import WebBase

class WebCertifications(WebBase):
### Certifications
    #TODO - this should be cleaned up to use DB functionality instead of filtering on webpage
    def showCertifications(self, message, barcodes, tools, show_table_header=True):
        return self.template('certifications.mako', message=message,
                             show_table_header=show_table_header,
                             barcodes=barcodes,
                             tools=tools,
                             members=self.engine.members,
                             certifications=self.engine.certifications.getUserList())

    @cherrypy.expose
    def certify(self, certifier_id):
        message = ''
        with self.dbConnect() as dbConnection:
            return self.template('certify.mako', message=message,
                                 certifier=self.engine.members.getName(dbConnection,
                                                                       certifier_id)[1],
                                 certifier_id=certifier_id,
                                 members_in_building=self.engine.visits.getMembersInBuilding(
                                     dbConnection),
                                 tools=self.engine.certifications.getListCertifyTools(dbConnection, certifier_id))

    @cherrypy.expose
    def certify_all(self, certifier_id):
        message = ''
        with self.dbConnect() as dbConnection:
            return self.template('certify.mako', message=message,
                                certifier=self.engine.members.getName(dbConnection,
                                    certifier_id)[1],
                                certifier_id=certifier_id,
                                members_in_building=self.engine.visits.getAllMembers(dbConnection),
                                tools=self.engine.certifications.getListCertifyTools(dbConnection, certifier_id))

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
            return self.template('certifications.mako', message=message,
                                 barcodes=self.engine.visits.getMemberBarcodesInBuilding(
                                     dbConnection),
                                 tools=self.engine.certifications.getAllTools(
                                     dbConnection),
                                 dbConnection=dbConnection,
                                 members=self.engine.members,
                                 certifications=self.engine.certifications.getUserList(dbConnection))

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
                barcodes = None
            if show_table_header == '0' or show_table_header.upper() == 'FALSE':
                show_table_header = False

            return self.template('certifications.mako', message=message,
                                    barcodes=barcodes,
                                    tools=self.engine.certifications.getToolsFromList(dbConnection,
                                                                                    tools),
                                    members=self.engine.members,
                                    dbConnection=dbConnection,
                                    certifications=self.engine.certifications.getUserList(dbConnection))
    @cherrypy.expose
    def all_certification_list(self):
        message = ''
        with self.dbConnect() as dbConnection:
            return self.template('certifications.mako', message=message,
                                 barcodes=None,
                                 tools=self.engine.certifications.getAllTools(
                                     dbConnection),
                                 members=self.engine.members,
                                 dbConnection=dbConnection,
                                 certifications=self.engine.certifications.getUserList(dbConnection))