<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Login</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>Login Page</H1>

<form action="loginAttempt">
   <input id="user_id" type="text" name="username" placeholder="Login Name" /><br />
   <input id="pass_id" class="password" type="password" name="password" placeholder="Password" /><br />
   <input type="submit" value="Login"/>
</fieldset>
</form>
