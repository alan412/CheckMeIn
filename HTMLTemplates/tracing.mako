<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Tracing</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>Tracing for ${displayName}</H1>

% for when, whom in dictVisits.items():
  <H2> ${when.strftime("%c")}
     <UL>
     %for person in whom:
        <LI>${person.displayName} (${person.barcode}) - ${person.email}</LI>
     % endfor
     </UL>
% endfor 
        