<%def name="scripts()">
<script>
window.onload = setTimeout(function(){location.href="/station"},1000*15*1);  // if still here in 30 seconds
</script>
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Keyholder</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>Change Keyholder</H1>
<P>
You have several choices, but be quick (15 second time limit):</P>
<UL>
<LI>Scan your button again or keyholder.<br/>   This means you are locking up and logs everyone out that has forgotten.
% if len(whoIsHere) > 0:
<br/><b>Make sure you are the only one in the building.</b>  The following people haven't checked out:
<UL>
% for member in whoIsHere:
<LI>${member}</LI>
% endfor
</UL>
% endif

<LI>Scan button of new Keyholder.<br/>  This makes them the keyholder.  Please give them the keyholder button
<LI>Let the page timeout.<br/> This means the old keyholder stays the keyholder.
</UL>
<form action="keyholder">
     <input id="member_id" type="text" name="barcode" size="8" autofocus placeholder="Member ID"/><br/>
</form>
