<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Teams</%def>
<%inherit file="base.mako"/>
<div>
${self.logo()}
<A style="text-align:right" HREF="/profile/logout">Logout ${username}</A><br/>
</div>
<br/>
<H1>${team_name}</H1>
<H3>Season starting ${firstDate.strftime("%d %b %y")}</H3>
   <form action="update">
  <fieldset>
    <legend>Who is in building?</legend>
    <br/>
    <table class="teamMembers">
      <tr><th>Name</th><th></th><th>In</th><th>Out</th></tr>
    % for member in members:
      <tr><td>${member.name}</td>
      <td>${"(Coach)" if member.type == TeamMemberType.coach else "(Mentor)" if member.type == TeamMemberType.mentor else "(Other)" if member.type == TeamMemberType.other else ""}
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
    <legend>Who was here during a team meeting</legend>
    <br/>
    <input type="hidden" name="team_id" value="${team_id}">
    <input id="date" type="date" name="date" value="${todayDate}"
                            min="${firstDate.isoformat()}" max="${todayDate}"/>
    <label for="startTime">Start Time:</label>
    <input id="time" type="time" name="startTime" value="18:00"/>
    <label for="endTime">End Time:</label>
    <input id="time" type="time" name="endTime" value="20:00"/><br/>
    <input type="submit" value="See Attendance"/>
  </fieldset>
</form>
<br/>

<br/>
<form action="addMember">
   <fieldset>
     <legend>Add Team Member</legend>
    <div>
      <input type="hidden" name="team_id" value="${team_id}">
      <select name="member" id="member">
          <option disabled selected value> -- select a member -- </option>
	   % for user in activeMembers:
	       <option value="${user[1]}">${user[0]} - ${user[1]}</option>
	   % endfor
		</select>
    </div>
    <div>
      <input type="radio" name="type" id="student" checked="checked" value="${int(TeamMemberType.student)}">
            <label class="normal" for="student">Student</label>
      <input type="radio" name="type" id="mentor" value="${int(TeamMemberType.mentor)}">
            <label class="normal" for="mentor">Mentor</label>
      <input type="radio" name="type" id="coach" value="${int(TeamMemberType.coach)}">
            <label class="normal" for="coach">Coach</label>   
      <input type="radio" name="type" id="other" value="${int(TeamMemberType.other)}">
            <label class="normal" for="other">Other</label>   
    </div> 
  <input type="submit" value="Add"/>
</fieldset>
</form>
<br/>
<form action="removeMember">
   <fieldset>
     <legend>Remove Team Member</legend>
    <div>
      <input type="hidden" name="team_id" value="${team_id}">
      <select name="member" id="member">
	   % for member in members:
	       <option value="${member.barcode}">${member.name}</option>
	   % endfor
		</select>
    </div>
  <input type="submit" value="Remove"/>
</fieldset>
</form>
<br/>
<form action="renameTeam">
<fieldset>
    <legend>Change Team Name</legend>
    <input type="hidden" name="team_id" value="${team_id}">
    <input name="newName" placeholder="${team_name}">
    <input type="Submit" value="Rename"/>
</fieldset>
</form>
<br/>

<form action="newSeason">
<fieldset>
   <legend>Make new season</legend>
    <div>
      <input type="hidden" name="team_id" value="${team_id}">
      <table>
      		<TR><TD>Start Date:</TD>
	      	<TD><input id="start_date" type="date" name="startDate" value="${todayDate}" max="${todayDate}"/></TD></TR>
      </table>
      <table>
      <tr><th>Name</th><th>Returning</th></tr>
	   % for member in members:
      <tr><td>${member.name}</td>
      <td>${"(Coach)" if member.type == TeamMemberType.coach else "(Mentor)" if member.type == TeamMemberType.mentor else "(Other)" if member.type == TeamMemberType.other else ""}</td>
      <td><input type="checkbox" value="${member.type}" name="${member.barcode}"></td></tr>
	   % endfor
      </table>
		</select>
    </div>
  <input type="submit" value="New Season"/>
</fieldset>
</form>
<br/>
<fieldset>
   <legend>All Seasons</legend>
   <H3>${seasons[0].getProgramId()}</H3>
   <UL>
     % for team in seasons:
     <LI><A HREF="/teams?team_id=${team.teamId}">${team.startDate.strftime("%d %b %y")} : ${team.name}</LI>
     % endfor
   </UL>
</fieldset>
