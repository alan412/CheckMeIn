<%def name="scripts()">
</%def>
<%def name="head()">
</%def>
<%def name="title()">Congratulations!!!</%def>
<%inherit file="base.mako"/>

<H1> ${memberName} is now certified as ${level} on ${tool}!!!</H1> 

<A HREF="/certify?certifier_id=${certifier_id}">Certify another</A>

