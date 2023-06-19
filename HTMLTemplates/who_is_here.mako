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

 %if makeForm:
 <form action="checkout_who_is_here">
 %endif
  <table class="members">
      % for member in whoIsHere:
        <TR><TD><input type="checkbox" name="${member.barcode}" value="out"/></TD><TD>${member.displayName}</TD>
        <TD>${member.start.strftime("%I:%M %p")}</TD></TR>
      % endfor
  </table>
%if makeForm:
<input type="submit" value="Check Out"/>
</form>
%endif