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
% if show_left_names:
   <TH></TH>
% endif
% for tool in tools:
   <TH>${tool[1]}</TH>
% endfor
% if show_right_names:
   <TH></TH>
% endif
</TR>
% endif
% for user, user_tools in certifications.items():
   <TR>
   % if show_left_names:
   <TD>${user_tools.displayName}</TD>
   % endif
   % for tool in tools:
      ${user_tools.getHTMLCellTool(tool[0]) | n}
   % endfor
   % if show_right_names:
   <TD>${user_tools.displayName}</TD>
   % endif
   </TR>
% endfor
</TABLE>