<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Links</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
% if barcode==None:
<H2><A HREF="/station">Main Station</A></H2>
<H2><A HREF="/guests">Guest Station</A></H2>
<H2><A HREF="/certifications">Certification Monitor</A></H2>
# TODO: This will allow you to set the certification monitor settings

<form action="/links">
       <td><select name="barcode" id="barcode">
	   % for user in activeMembers:
	       <option value="${user[1]}">${user[0]} - ${user[1]}</option>
	   % endfor
		</select></td></tr>
        <input type="submit" value="Show Links"/>
</form>
% else:
<H1>${displayName}</H1>
   % if inBuilding:
      <H2><A HREF="/station/checkout?barcode=${barcode}">Check out</A></H2>
   % else:
      <H2><A HREF="/station/checkin?barcode=${barcode}">Check in</A></H2>
   % endif
   <H2><A HREF="/">See who is here</A></H2>

   % if role.isKeyholder() or role.isAdmin():
      <H2><A HREF="/profile/">Profile</A></H2>
   % endif

   % if role.isAdmin():
   <H1>Admin Tasks</H1>
      <H2><A HREF="/admin">Admin Console</A></H2>
      <H2><A HREF="/admin/users">Manage Users</A></H2>
      <H2><A HREF="/reports">Reports</A></H2>
   % endif

   % if role.isShopCertifier():
   <H1>Shop Certifier Tasks</H1>


   % endif


% endif