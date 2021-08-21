<%def name="scripts()">
<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
<script>
function deleteUser(userName, barcode) {
		if (confirm("OK to delete account for " + userName + "?")) {
			window.location.href = "deleteUser?barcode="+barcode;
		}
}
function changeAccess(userName, barcode, keyholder, admin, certifier, coach){
	$('#dlgUsername').html(userName);
	$('#dlgKeyholder').prop('checked', keyholder);
	$('#dlgAdmin').prop('checked', admin);
	$('#dlgCertifier').prop('checked', certifier);
	$('#dlgCoach').prop('checked', coach);

    var dWidth = $(window).width() * 0.8;
	$("#changeAccessDialog").dialog({
        autoOpen: false,
        modal: true,
		width: dWidth,
        buttons: {
            " Cancel ": function() {
                $(this).dialog('close');
            },
            " Ok ": function() {
                $(this).dialog('close');
				requestStr = 'changeAccess?barcode='+barcode+'&admin='
				if ($('#dlgAdmin').is(':checked')) {
					requestStr += '1'
				}else{
					requestStr += '0'
				}
				requestStr += '&keyholder='
				if ($('#dlgKeyholder').is(':checked')) {
					requestStr += '1'
				}else{
					requestStr += '0'
				}
				requestStr += '&certifier='
				if ($('#dlgCertifier').is(':checked')) {
					requestStr += '1'
				}else{
					requestStr += '0'
				}
				requestStr += '&coach='
				if ($('#dlgCoach').is(':checked')) {
					requestStr += '1'
				}else{
					requestStr += '0'
				}
				window.location.href = requestStr;
			}
		}
	});
	$("#changeAccessDialog").dialog( "open");
}
</script>			
</%def>
<%def name="head()">
<link href = "https://code.jquery.com/ui/1.10.4/themes/ui-lightness/jquery-ui.css"
         rel = "stylesheet">
</%def>

<%def name="title()">CheckMeIn Users</%def>
<%inherit file="base.mako"/>
${self.logo()}
<A style="text-align:right" HREF="/profile/logout">Logout ${username}</A><br/>
	  <br/>
	  <fieldset>
	    <legend>Current Users with Roles</legend>
		<table class="users" width="100%">
			<tr>
				<th align="left">UserName</th>
				<th align="left">Barcode</th>
				<th align="left">Role</th>
				<th>Actions</th>
			</tr>
			% for user in users:
			<TR class="users" uid="${user}">
				<TD align="left">${user}</TD>
				<TD align="left">${users[user].get('barcode','')} 
				( ${users[user].get('displayName', '')} )</TD>
        		<TD align="left">${users[user].get('role','')}</TD>
				<TD align="center"><button name="Delete" onclick="deleteUser('${user}', '${users[user].get('barcode','')}')">Delete</button>
					<button name="ChangeAccess" onclick="changeAccess('${user}', '${users[user].get('barcode','')}', 
						${users[user].get('role',0).isKeyholder()},
						${users[user].get('role',0).isAdmin()},
						${users[user].get('role',0).isShopCertifier()},
						${users[user].get('role',0).isCoach()},
						)">Change Access</button>
			</TR>
			% endfor
		</table>
	</fieldset>
	<fieldset>
	<legend>Add User with Roles</legend>
    <form action="addUser">
       <table>
       <tr><td>Username:</td>
       <td><input name="user" id="username"></td></tr>
       <tr><td>Barcode:</td>
       <td><select name="barcode" id="barcode">
	   % for barcode in nonAccounts:
	       <option value="${barcode}">${nonAccounts[barcode]} - ${barcode}</option>
	   % endfor
		</select></td></tr>
       <tr><td colspan=2>Access type:</td>
       <td><input type="checkbox" id="keyholder" name="keyholder" value="1" checked/>Keyholder</td>
       <td><input type="checkbox" id="admin" name="admin" value="1"/>Admin</td>
	   <td><input type="checkbox" id="certifier" name="certifier" value="1"/>Shop Certifier</td>
	   <td><input type="checkbox" id="coach" name="coach" value="1"/>Coach</td>
      </table>
      <input type="submit" value="Add"/>
      </form>
	  </fieldset>
<br/>
<div id="changeAccessDialog" title="Change Access" style="display:none;">
<H2 id="dlgUsername"></H2>
<label><input type="checkbox" id="dlgAdmin" />Admin</label>
<label><input type="checkbox" id="dlgKeyholder" />Keyholder</label>
<label><input type="checkbox" id="dlgCertifier" />Certifier</label>
<label><input type="checkbox" id="dlgCoach" />Coach</label>
</div>
<hr/>
To add feature requests or report issues, please go to:<A HREF="https://github.com/alan412/CheckMeIn/issues">https://github.com/alan412/CheckMeIn/issues</A>