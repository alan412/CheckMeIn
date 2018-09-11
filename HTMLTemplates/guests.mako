<%def name="scripts()">
<script>
  window.onload = setTimeout(function () { location.href = "guests" }, 1000 * 60 * 10);  // if still here in 10 minutes 
</script>
</%def>
<%def name="head()">
</%def>
<%def name="title()">CheckMeIn - Guest Station</%def>
<%inherit file="base.html"/>
<table class="header">
<TR>
  <TD><IMG ALT="TFI Logo" SRC="static/TFI-logo-smaller.png" WIDTH="150"/></TD>
  <TD><H2>Guest Station</H2></TD>
</TR>
</table>

%if message:
  <H1>${message}</H1>
%endif

<TABLE>
  <TR>
    <TD style="text-align:center"><button class="btnGuest" id="firstTime">First time guest</button></TD>
    <TD style="text-align:center"><button class="btnGuest" id="returning">Returning guest</button></TD>
  </TR>
  <TR><TD COLSPAN=2 style="text-align:center"><button class="btnGuest" id="leaving">Leaving building</button></TD></TR>
</TABLE>

<script>
  $(document).ready(function () {
    $("button#firstTime").click(function () {
      $("#modal-header").html("First Time Guests")
      $("#modal-body").html('<form action = "addGuest">' +
        'We are glad to have you visit The Forge Initiative. We hope you have a lot of fun ' +
        'here learning and creating.In order to do that, we need a little information from you ' +
        'first.<br/>' +
        '<table>' +
        '<tr><td class="label">First Name:</td>' +
        '<td><input autofocus type="text" name="first" placeholder="First"></td></tr>' +
        '<tr><td class="label">Last Name:</td>' +
        '<td><input type="text" name="last" placeholder="Last"></td></tr>' +
        '<tr><td class="label">E-mail:</td>' +
        '<td><input type="text" name="email" placeholder="me@mail.com"></td></tr>' +
        '<tr><td class="label">What brings you here today?</TD>' +
        '<td><input type="radio" name="reason" value="Tour" checked="checked">Tour / Introduction<br/>' +
        '<input type="radio" name="reason" value="Event">Scheduled event - program, workshop, camp or event<br />' +
        '<input type="radio" name="reason" value="guest">Guest of a member<br />' +
        '<input type="radio" name="reason" value="team">Team meeeting<br />' +
        '<input type="radio" name="reason" value="">Other <input type="text" name="other_reason" />' +
        '</td></tr>' +
        '</table><br/>' +
        '< CENTER > <input id="register" type="submit" value="Register" /></CENTER ></form>');
      modal.style.display = "block";
    });
    $("button#returning").click(function () {
      $("#modal-header").html("Returning Guests")
      $("#modal-body").html('<form action = "returnGuest">' +
        'Please select your name from the list.   (List only has guests that ' +
        'have used this system before.) <br/>' +
        '<select name="guest_id">' +
   % for guest in guestList:
        '<option value="${guest.guest_id}">${guest.displayName}</option>' +
   % endfor
      '</select><input type="submit" value="Check In"/></form>');
    modal.style.display = "block"
  });
  $("button#leaving").click(function () {
    $("#modal-header").html("Leaving Building")
    $("#modal-body").html('<form action = "leaveGuest">' +
      'We hope you enjoyed your time here.   Please select your name from the list.<br/>' +
      '<select name="guest_id">' +
   % for guest in inBuilding::
      '<option value="${guest.guest_id}">${guest.displayName}</option>' +
   % endfor
    '</select><input type="submit" value="Check Out"/></form>');
  modal.style.display = "block";
    });
  };
</script>