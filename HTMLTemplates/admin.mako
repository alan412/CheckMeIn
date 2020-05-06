<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Admin</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>Admin Page</H1>

<br/>
<form action="bulkAddMembers" method="post" enctype="multipart/form-data">
<fieldset>
    <legend>Bulk add members</legend>
          <input type="file" ID="csvFile" name="csvfile" accept=".csv"/>
    <br/>
    <input type="submit" value="Add Members"/>
  </fieldset>
</form>

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

<H2><A HREF="/reports/">Reports</A></H2>


<form action="createTeam">
  <fieldset>
    <legend>Create a Team</legend>
    <div>
    <label for="team_name">Team Name:</label>        
    <input type="text" name="team_name" placeholder="FLL447-2018"/><br/>
    </div>    
    <input type="submit" value="Create Team"/>
  </fieldset>
</form>
<form action="team">
  <fieldset>
    <legend>Admin Team</legend>
    <div>
    <label for="team_id">Team Name:</label>        
    <select name="team_id">
   % for team in teamList:
        <option value="${team[0]}">${team[1]}</option>
   % endfor
    </select><br/>
    </div>    
    <input type="submit" value="Admin Team"/>
  </fieldset>
</form>
<hr/>
To add feature requests or report issues, please go to:<A HREF="https://github.com/alan412/CheckMeIn/issues">https://github.com/alan412/CheckMeIn/issues</A>