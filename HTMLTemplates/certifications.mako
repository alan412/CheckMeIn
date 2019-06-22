<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">Certifications</%def>
<%inherit file="base.mako"/>

<TABLE>
<TH>
   <TD>Name</TD>
% for tool in tools:
   <TD>${tool[1]}</TD>
% endfor
</TH>
</TABLE>
