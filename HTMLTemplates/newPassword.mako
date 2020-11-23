<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn - New Password</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>New Password</H1>

<form action="newPassword">
<fieldset>
   <legend>New Password</legend>
   <input type="hidden" name="user" value="${user}">
   <input type="hidden" name="token" value="${token}">
   <input id="pass1" class="password" type="password" name="newPass1" placeholder="Password" /><br />
   <input id="pass2" class="password" type="password" name="newPass2" placeholder="Password (again)" /><br />
   <input type="submit" value="Login"/>
</fieldset>
</form>


