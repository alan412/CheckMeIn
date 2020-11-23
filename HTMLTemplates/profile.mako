<%def name="scripts()">
<script>
function deleteDevice(name, mac) {
		if (confirm("OK to delete device " + name + "?")) {
			window.location.href = "delDevice?mac="+mac;
		}
}
</script>			
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Profile</%def>
<%inherit file="base.mako"/>
${self.logo()}
<A style="text-align:right" HREF="/profile/logout">Logout ${username}</A><br/>
<form action="changePassword">
    <fieldset>
   <legend>Change Password</legend>
   <input class="password" type="password" name="oldPass" placeholder="Old Password" /><br />
   <input class="password" type="password" name="newPass1" placeholder="New Password" /><br />
   <input class="password" type="password" name="newPass2" placeholder="New Password (again)" /><br />
   <input type="submit" value="Login"/>
</fieldset>
</form>
<br/>
	<fieldset>
	<legend>Add Device</legend>
    <form action="addDevice">
       <table>
       <tr><td>Device Name:</td>
       <td><input type="text" id="name" name="name" placeholder="phone"></td></tr>
       <tr><td>MAC:</td>
       <td><input type="text" id="mac" name="mac" placeholder="11:22:33:44:55:66"></td></tr>
      </table>
      <input type="submit" value="Add"/>
    </form>
	</fieldset>
	<br/>
	<fieldset>
	    <legend>Current Devices</legend>
		<table class="devices" width="100%">
			<tr>
				<th align="left">Device Name</th>
				<th align="left">MAC</th>
				<th></th>
			</tr>
			% for device in devices:
			<TR class="devices">
				<TD align="left">${device.name}</TD>
				<TD align="left">${device.mac}</TD>
				<TD align="center"><button name="Delete" onclick="deleteDevice('${device.name}', '${device.mac}')">Delete</button></TD>
			</TR>
			% endfor
		</table>
	</fieldset>
	<br/>