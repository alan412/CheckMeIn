<%def name="scripts()">
<script>
window.onload = setTimeout(function(){location.href="station"},1000*30*1);  // if still here in 30 seconds
</script>
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Keyholder</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>Keyholder Checkout</H1>
<P>
You are the active keyholder</P>
<P>
You can either checkout (which logs out all that have forgotten) or cancel and go find 
another keyholder and then checkout.
% if len(whoIsHere) > 0:
<br/><b>Make sure you are the only one in the building.</b>  The following people haven't checked out:
<UL>
% for member in whoIsHere:
<LI>${member}</LI>
% endfor
</UL>
% endif
<input type="button" onclick="location.href='/station/keyholder?barcode=${barcode}';" value="Checkout" />
<input type="button" onclick="location.href='/station/';" value="Cancel"
