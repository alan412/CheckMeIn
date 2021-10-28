<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Team Report</%def>
<%inherit file="base.mako"/>
<CENTER>
${self.logo()}<br/>
</CENTER>
<H1> Team List </H1>
<UL>
% for team in teams:
   <LI>${team.getProgramId()} - ${team.name}
   <UL>
   % for member in team.members: 
     % if member.type >= 0: 
     <LI>${member.name} ${member.typeString()}</LI>
     % endif %
   % endfor %
   </UL></LI>
% endfor 
</UL>