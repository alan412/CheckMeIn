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
% else

% endif