<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Login</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>Login Page</H1>

<form action="loginAttempt">
<fieldset>
   <legend>Login</legend>
   <input id="user_id" type="text" name="username" placeholder="Login Name" /><br />
   <input id="pass_id" class="password" type="password" name="password" placeholder="Password" /><br />
   <input type="submit" value="Login"/>
</fieldset>
</form>

<form action="forgotPassword">
<fieldset>
   <legend>Forgot Password</legend>
   If you don't remember your user name, you can put your email in here as well.<br/>
   <input id="user_id" type="text" name="user" placeholder="Login Name" /><br />
   <input type="submit" value="Forgot password"/>
</fieldset>
</form>


