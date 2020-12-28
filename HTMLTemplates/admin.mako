<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Admin</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<A style="text-align:right" HREF="/profile/logout">Logout ${username}</A>
<H1>Admin Page</H1>

<P style="margin-top: 1cm; margin-bottom: 1cm">
<A HREF="users"><button style="margin-right: 1cm">Manage Users</button></a>
<A HREF="/reports"><button>Reports</button></a>
<A HREF="teams"><button style="margin-right: 1cm">Manage Teams</button></a>
</P>

<form action="bulkAddMembers" method="post" enctype="multipart/form-data">
<fieldset>
    <legend>Bulk add members</legend>
          <input type="file" ID="csvFile" name="csvfile" accept=".csv"/>
    <br/>
    <input type="submit" value="Add Members"/>
  </fieldset>
</form>
<br/>

<form action="oops">
   <fieldset>
     <legend>Oops</legend>
   Keyholder accidentally signed out.  Move all FORGOT for today back to in.<br/>
  <input type="submit" value="Oops!"/>
</fieldset>
</form>

<H2>Fix "forgot" data</H2>
%if len(forgotDates):
  <FORM action="fixData">
  <SELECT id="date-select" name="date">
%for date in forgotDates:
    <OPTION value="${date}">${date}</OPTION>
%endfor
  </SELECT>
  <input type="submit" value="Fix Data"/>
</form>
%else:
  <P>Wow!  No dates that haven't been cleaned up!!</P>
%endif

<hr/>
To add feature requests or report issues, please go to:<A HREF="https://github.com/alan412/CheckMeIn/issues">https://github.com/alan412/CheckMeIn/issues</A>