<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">Tool Certification</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>Tool Certification</H1>
<H2>Certifier: ${certifier} </H2>

<br/>
<form action="addCertification">
  <fieldset>
    <legend>Add Tool Certification</legend>
    <table>
      <tr><td>Who to certify:</td>
      <td><select name="member_id">
        % for member in members_in_building:
            <option value="${member[1]}">${member[0]} (${member[1]})</option>
        % endfor
        </select></td></tr>
      <tr><td><label for="tool_id">Tools:</label></td><td>        
    <select name="tool_id">
   % for tool in tools:
        <option value="${tool[0]}">${tool[1]}</option>
   % endfor
    </select></td><br/>
    </tr>
      <tr><td><label for="level">New Level:</label></td>
          <td><select name="level">
            <option value="1">BASIC (Red dot)</option>
            <option value="10">CERTIFIED (Green dot)</option>
            <option value="20">DOF</option>
            <option value="30">INSTRUCTOR</option>
            <option value="40">CERTIFIER</option>
    </select></td></tr>
    <tr><td>
    <input type="submit" value="Add Certification">
    </td></tr>
    </table>
  </fieldset>
</form>
