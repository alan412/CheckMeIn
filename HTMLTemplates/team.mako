<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Teams</%def>
<%inherit file="base.mako"/>
${self.logo()}
<br/>
<H1>${team_name}</H1>
   <form action="update">
  <fieldset>
    <legend>Update who is in building</legend>
    <br/>
    <table class="teamMembers">
      <tr><th>Name</th><th>In</th><th>Out</th></tr>
    % for member in members:
      <tr><td>${member.name}</td>
      % if member.present:
        <td><input type="radio" name="${member.barcode}" checked="checked"value="in"></td>
        <td><input type="radio" name="${member.barcode}" value="out"></td>
      % else:
        <td><input type="radio" name="${member.barcode}" value="in"></td>
        <td><input type="radio" name="${member.barcode}" checked="checked" value="out"></td>
      % endif
      </tr>
    % endfor
    </table>
    <input type="hidden" name="team_id" value="${team_id}">
    <input type="submit" value="Update"/>
  </fieldset>
    </form>
<br/>
   <form action="certifications">
  <fieldset>
    <legend>Tool certifications</legend>
    <br/>
    <input type="hidden" name="team_id" value="${team_id}">
    <input type="submit" value="See Tool Certifications"/>
  </fieldset>
    </form>
  <br/>
<form action="attendance">
  <fieldset>
    <legend>See who was here during a team meeting</legend>
    <br/>
    <input type="hidden" name="team_id" value="${team_id}">
    <input id="date" type="date" name="date" value="${todayDate}"
                            min="${firstDate}" max="${todayDate}"/>
    <label for="startTime">Start Time:</label>
    <input id="time" type="time" name="startTime" value="18:00"/>
    <label for="endTime">End Time:</label>
    <input id="time" type="time" name="endTime" value="20:00"/><br/>
    <input type="submit" value="See Attendance"/>
  </fieldset>
</form>
<br/>

<br/>
<form action="addMembers">
   <fieldset>
     <legend>Add Team Members</legend>
     <P>This needs to be the barcodes for each member.</P>
      <input type="hidden" name="team_id" value="${team_id}">
      <label for="students" style="vertical-align:top">Students:</label>
      <textarea rows="4" cols="40" name="students" placeholder="100090 100091"></textarea><br/>
      <label for="mentors" style="vertical-align:top">Mentors (non-coaches):</label>
      <textarea rows="2" cols="40" name="mentors" placeholder="100090 100091"></textarea><br/>      
      <label for="coaches">Coaches:</label>
      <textarea rows="1" cols="40" name="coaches" placeholder="100090 100091"></textarea><br/>            
   <br/>
  <input type="submit" value="Add Team Members"/>
</fieldset>
</form>
<br/>