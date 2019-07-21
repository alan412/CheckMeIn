<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">Certifications</%def>
<%inherit file="base.mako"/>

<TABLE>
<TR>
   <TD>Name</TD>
% for tool in tools:
   <TD>${tool[1]}</TD>
% endfor
</TR>
% for user, user_tools in certifications.items():
   % if not barcodes or (user in barcodes):
   <TR>
   <TD>${members.getName(user)[1]}</TD>
   % for tool in tools:
      ${user_tools.getHTMLCellTool(tool[0]) | n}
   % endfor
   </TR>
   % endif
% endfor
</TABLE>