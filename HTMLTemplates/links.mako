<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Links</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
% if barcode==None:
<H3><A HREF="/station">Main Station</A></H3>
<H3><A HREF="/guests">Guest Station</A></H3>
<H3><A HREF="/certifications">Certification Monitor</A></H3>
<H3><A HREF="/whoishere">Who is at BFF</A></H3>
<H3><A HREF="/profile/login">Login</A></H3>

<!-- TODO: This will allow you to set the certification monitor settings -->

<form action="/links">
       <td><select name="barcode" id="barcode">
	   % for user in activeMembers:
	       <option value="${user[1]}">${user[0]} - ${user[1]}</option>
	   % endfor
		</select></td></tr>
        <input type="submit" value="Show Links"/>
</form>
<HR/>
<H3><A HREF="/certifications/all">See list of all certifications</A></H3>
% else:
<H1>${displayName}</H1>
   
   % if inBuilding:
      <H3><A HREF="/station/checkout?barcode=${barcode}">Check out of BFF</A></H3>
   % else:
      <H3><A HREF="/station/checkin?barcode=${barcode}">Check into BFF</A></H3>
   % endif
   <H3><A HREF="/certifications/user?barcode=${barcode}">My Shop Certifications</A></H3>


   % if role.isKeyholder() or role.isAdmin() or role.isCoach():
      <H3><A HREF="/profile/">Profile</A></H3>
   % endif
   
   % if role.isKeyholder():
   <H2>Keyholder Tasks</H2>
      <H3><A HREF="/station/makeKeyholder?barcode=${barcode}">Make ME Keyholder</A>
      <H3><A HREF="http://192.168.1.10">Door App (Works ONLY when at BFF)</A>
      <H3><A HREF="/admin/oops">Oops (Didn't meant to close building)</A></H3>
   % endif

   % if role.isCoach():
   <H2>Coach Tasks</H2>
      % for team in activeTeamsCoached:
         <H3><A HREF="/teams?team_id=${team.teamId}">${team.getProgramId()} - ${team.name}</A>
      % endfor
   % endif

   % if role.isAdmin():
   <H2>Admin Tasks</H2>
      <H3><A HREF="/admin">Admin Console</A></H3>
      <H3><A HREF="/admin/users">Manage Users</A></H3>
      <H3><A HREF="/admin/teams">Manage Teams</A></H3>
      <H3><A HREF="/reports">Reports</A></H3>
      <hr/>
      To add feature requests or report issues, please go to:<A HREF="https://github.com/alan412/CheckMeIn/issues">https://github.com/alan412/CheckMeIn/issues</A>
      <br/>
   % endif

   % if role.isShopCertifier():
   <H2>Shop Certifier Tasks</H2>
     <H3><A HREF="/certifications/certify">Certify those in building</A></H3>
     <H3><A HREF="/certifications/certify?all=True">Certify any member</A></H3>
     <H3><A HREF="/certifications/all">See list of all certifications</A></H3>
   % endif
   <HR/>
   <H3><A HREF="/whoishere">See who is here</A></H3>
   <H3><A HREF="/links">Generic Links</A></H3>
   <H3><A HREF="/certifications">Certification Monitor</A></H3>
   <H3><A HREF="/profile/login">Login</A></H3>
% endif