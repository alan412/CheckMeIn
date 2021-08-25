<%def name="scripts()">
</%def>
<%def name="head()">
</%def>
<%def name="title()">Congratulations!!!</%def>
<%inherit file="base.mako"/>

<H1> ${memberName} is now certified as ${level} on ${tool}!!!</H1> 

<A HREF="/certifications/certify">Certify another</A></br>
<A HREF="/links?barcode=${certifier_id}>My links</A></br>