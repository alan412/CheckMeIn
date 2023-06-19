<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Links</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
% if barcode==None:
<H2>Links per member</H2>
<form action="/links">
       <td><select name="barcode" id="barcode">
          <option disabled selected value> -- select a member -- </option>
	   % for user in activeMembers:
	       <option value="${user[1]}">${user[0]} - ${user[1]}</option>
	   % endfor
		</select></td></tr>
        <input type="submit" value="Show Links"/>
</form>
<HR/>
% else:
<H1>${displayName} <span class="small">(${barcode})</span></H1>
   <fieldset><legend>Personal</legend>
   <UL>
   % if inBuilding:
      <LI><A HREF="/station/checkout?barcode=${barcode}">Check out of BFF</A>
   % else:
      <LI><A HREF="/station/checkin?barcode=${barcode}">Check into BFF</A>
   % endif
   <LI><A HREF="/certifications/user?barcode=${barcode}">My Shop Certifications</A>
   % if role.value != 0:
      <LI><A HREF="/profile/">Change Password</A>
      <LI><A HREF="/profile/logout">Logout</A>
   % else:
      <LI><A HREF="/profile/login">Login</A>
   % endif
   </fieldset><br/>
   <fieldset><legend>General</legend>
   <UL>
      <LI><A HREF="/whoishere">See who is at BFF</A>
      <LI><A HREF="https://calendar.google.com/calendar/embed?src=h75eigkfjvngvpff1dq0af74mk%40group.calendar.google.com&ctz=America%2FNew_York">TFI Calendar</A>
      <LI><A HREF="https://app.theforgeinitiative.org/">Forge Member App</A>
   </UL>
   </fieldset><br/>

   % if role.isKeyholder():
   <fieldset>
   <legend>Keyholder</legend>
   <UL>
      <LI><A HREF="http://192.168.1.10">Downstairs Door (Works ONLY when at BFF)</A></LI>
      <LI><A HREF="http://10.0.0.10">Upstairs Door (Works ONLY when at BFF)</A></LI>

      <LI><A HREF="/station/makeKeyholder?barcode=${barcode}">Make ME Keyholder</A></LI>
      <LI><A HREF="/station/updatePresent">Update who is in building</A></LI>
      <LI><A HREF="/admin/oops">Oops (Didn't meant to close building)</A></LI>
   </fieldset><br/>
   % endif

   % if role.isCoach():
   <fieldset><legend>Coach</legend>
      <UL>
      % for team in activeTeamsCoached:
         <LI><A HREF="/teams?team_id=${team.teamId}">${team.getProgramId()} - ${team.name}</A>
      % endfor
      </UL>
   </fieldset><br/>
   % endif

 % if role.isShopCertifier():
 <fieldset><legend>Shop Certifier</legend>
   <UL>
     <LI><A HREF="/certifications/certify">Certify those in building</A>
     <LI><A HREF="/certifications/certify?all=True">Certify any member</A>
     <LI><A HREF="/certifications">List of certifications for those in building</A>
     <LI><A HREF="/certifications/all">See list of all certifications</A>
   </UL>
   % endif
   </fieldset><br/>

   % if role.isAdmin():
   <fieldset><legend>Admin</legend>
   <UL>
      <LI><A HREF="/admin">Admin Console</A>
      <LI><A HREF="/admin/users">Manage Users</A>
      <LI><A HREF="/admin/teams">Manage Teams</A>
      <LI><A HREF="/reports">Reports</A>
   </UL>
   </fieldset><br/>
   % endif
% endif
<fieldset><legend>BFF Stations</legend>
<UL>
   <LI><A HREF="/station">Main Station</A></LI>
   <LI><A HREF="/guests">Guest Station</A></LI>
   <LI><A HREF="/certifications">Certification Monitor</A></LI>
</UL>
</fieldset></br/>
<hr/>
   To add feature requests or report issues, please go to:<A HREF="https://github.com/alan412/CheckMeIn/issues">https://github.com/alan412/CheckMeIn/issues</A>
<br/>