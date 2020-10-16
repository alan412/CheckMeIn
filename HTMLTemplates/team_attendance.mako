<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Teams</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>${team_name}</H1>

<form action="teamAttendance">
  <fieldset>
    <legend>See who was here during a team meeting</legend>
    <br/>
    <input type="hidden" name="team_id" value="${team_id}">
    <input id="date" type="date" name="date" value="${date}"
                            min="${firstDate}" max="${todayDate}"/>
    <label for="startTime">Start Time:</label>
    <input id="time" type="time" name="startTime" value="${startTime}"/>
    <label for="endTime">End Time:</label>
    <input id="time" type="time" name="endTime" value="${endTime}"/><br/>
    <input type="submit" value="See"/>
  </fieldset>
</form>
<br/>
<H2>Members here for meeting on ${date} from ${startTime} - ${endTime}</H2>
<H3>Total: ${len(membersHere)}</H3>
<UL>
%for member in membersHere:
    <LI>${member}</LI>
%endfor
</UL>

