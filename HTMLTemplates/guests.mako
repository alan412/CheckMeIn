<%def name="scripts()">
<script>
  window.onload = setTimeout(function () { location.href = "guests" }, 1000 * 60 * 10);  // if still here in 10 minutes 
</script>
</%def>
<%def name="head()">
</%def>
<%def name="title()">CheckMeIn - Guest Station</%def>
<%inherit file="base.mako"/>
<table class="header">
<TR>
  <TD style="text-align:center"><IMG ALT="TFI Logo" SRC="static/TFI-logo-smaller.png" WIDTH="200"/></TD>
  <TD style="text-align:center"><H1>Guest Station</H1></TD>
  <TD style="text-align:center"><IMG ALT="TFI Logo" SRC="static/TFI-logo-smaller.png" WIDTH="200"/></TD>
</TR>
</table>

%if message:
  <H1>${message}</H1>
%endif

<TABLE class="header">
  <TR><TD style="height: 50px"></TD></TR>
  <TR>
    <TD style="text-align:center"><button class="btnGuest" id="firstTime">First time guest</button></TD>
    <TD style="text-align:center"></TD>
    <TD style="text-align:center"><button class="btnGuest" id="returning">Returning guest</button></TD>
  </TR>
  <TR><TD style="height: 50px"></TD></TR>
  <TR><TD COLSPAN=3 style="text-align:center"><button class="btnGuest" id="leaving">Leaving building</button></TD></TR>
</TABLE>

<script>
	// Get the modal
	var modal = document.getElementById('modal');
	// Get the <span> element that closes the modal
	var span = document.getElementsByClassName("close")[0];

  $(document).ready(function () {
    $("button#firstTime").click(function () {
      $("#modal-header").html("First Time Guests");
      $("#modal-body").html('<form action = "addGuest">' +
        'We are glad to have you visit The Forge Initiative. We hope you have a lot of fun ' +
        'here learning and creating. In order to do that, we need a little information from you ' +
        'first.<br/>' +
        '<table>' +
        '<tr><td class="label">First Name:</td>' +
        '<td><input autofocus type="text" name="first" placeholder="First"></td></tr>' +
        '<tr><td class="label">Last Name:</td>' +
        '<td><input type="text" name="last" placeholder="Last"></td></tr>' +
        '<tr><td class="label">E-mail:</td>' +
        '<td><input type="text" name="email" placeholder="me@mail.com"></td></tr>' +
        '<tr><td class="label">Subscribe to e-mail newsletter?</td>' +
        '<td><input type="radio" name="newsletter" value="1" checked>Yes!  ' +
        '<input type="radio" name="newsletter" value="0">No</td></tr>' +
        '<tr><td class="label">What brings you here today?</TD>' +
        '<td><input type="radio" name="reason" value="Tour" checked="checked">Tour / Introduction<br/>' +
        '<input type="radio" name="reason" value="Event">Scheduled event - program, workshop, camp or event<br />' +
        '<input type="radio" name="reason" value="guest">Guest of a member<br />' +
        '<input type="radio" name="reason" value="team">Team meeeting<br />' +
        '<input type="radio" name="reason" value="">Other <input type="text" name="other_reason" />' +
        '</td></tr>' +
        '</table><br/>' +
        '<CENTER> <input class="button" id="register" type="submit" value="Register" /></CENTER ></form>');
      modal.style.display = "block";
    });
    $("button#returning").click(function () {
      $("#modal-header").html("Returning Guests");
      $("#modal-body").html('<form action = "returnGuest">' +
        'Please select your name from the list.   (List only has guests that ' +
        'have used this system before.) <br/>' +
        '<select name="guest_id">' +
   % for guest in guestList:
        '<option value="${guest.guest_id}">${guest.displayName}</option>' +
   % endfor
      '<CENTER></select><br/><br/><input class="button" type="submit" value="Check In"/></CENTER></form>');
    modal.style.display = "block"
  });
  $("button#leaving").click(function () {
    $("#modal-header").html("Leaving Building");
    $("#modal-body").html('<form action = "leaveGuest">' +
      '<br/>We hope you enjoyed your time here.   Please select your name from the list.<br/>' +
      '<select name="guest_id">' +
   % for guest in inBuilding:
      '<option value="${guest.guest_id}">${guest.displayName}</option>' +
   % endfor
    '<CENTER></select><br/><br/><input type="submit" class="button" value="Check Out"/></CENTER></form>');
  modal.style.display = "block";
    });
  });
  // When the user clicks on <span> (x), close the modal
	span.onclick = function () {
		modal.style.display = "none";
	}
	// When the user clicks anywhere outside of the modal, close it
	window.onclick = function (event) {
		if (event.target == modal) {
			modal.style.display = "none";
		}
	}
	// Handle ESC key (key code 27)
	document.addEventListener('keyup', function (e) {
		if (e.keyCode == 27) {
			modal.style.display = "none";
		}
	});
</script>