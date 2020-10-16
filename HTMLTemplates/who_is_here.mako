<%def name="scripts()">
</%def>
<%def name="head()">
</%def>
<%def name="title()">CheckMeIn - Who is here</%def>
<%inherit file="base.mako"/>
<table class="header">
<TR>
  <TD>${self.logo()}</TD>
  <TD><input type="button" value="Refresh" onClick="document.location.reload(true)"/></TD>
</TR>
</table>
  <H2>Checked in at ${now.strftime("%I:%M %p")}:</H2>
  Current Keyholder: ${keyholder}
  % if len(whoIsHere) == 1:
  <H2>1 person</H2>
  % else:
  <H2>${len(whoIsHere)} people</H2>
  % endif

  <table class="members">
      % for member in whoIsHere:
        <TR><TD><input type="checkbox"/></TD><TD>${member}</TD></TR>
      % endfor
  </table>
