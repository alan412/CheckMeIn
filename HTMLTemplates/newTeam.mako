<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">Create Team</%def>   
<%inherit file="base.mako"/>

<form action="new">
  <fieldset>
    <legend>Create a Team</legend>
    <div>
    Program Info: 
    <input type="text" name="program_name" value="${programName}"/>
    <input type="number" name="program_number" value="${programNumber}"/>
    </div>  
    <div>
    <br/>
    Team Name:        
    <input type="text" name="team_name" placeholder="Team Pyrotech" />
    </div>
    <br/>
  
    <input type="submit" value="Create Team"/>
  </fieldset>
</form>
