<%def name="scripts()">
</%def>
<%def name="head()">
<meta http-equiv="refresh" content="60">
</%def>

<%def name="title()">Certifications</%def>
<%inherit file="base.mako"/>


% if message:
<H1>${message}</H1>
% endif

<TABLE class="certifications">
% if show_table_header:
<TR>
% if show_name:
   <TH></TH>
% endif
% for tool in tools:
   <TH>${tool[1]}</TH>
% endfor
</TR>
% endif
% for user, user_tools in certifications.items():
   <TR>
   % if show_name:
   <TD>${user_tools.displayName}</TD>
   % endif
   % for tool in tools:
      ${user_tools.getHTMLCellTool(tool[0]) | n}
   % endfor
   <TD>${user_tools.displayName}</TD>
   </TR>
% endfor
</TABLE>