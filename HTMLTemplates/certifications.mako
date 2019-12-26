<%def name="scripts()">
</%def>
<%def name="head()">
<meta http-equiv="refresh" content="60">
</%def>

<%def name="title()">Certifications</%def>
<%inherit file="base.mako"/>

<TABLE class="certifications">
<TR>
   <TH></TH>
% for tool in tools:
   <TH>${tool[1]}</TH>
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