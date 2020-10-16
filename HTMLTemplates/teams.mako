<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Teams</%def>   
<%inherit file="base.mako"/>

<H2>List of active teams</H2>
<UL>
   % for team in teamList:
        <LI><A HREF="/teams/${team.getProgramId()}">${team.getProgramId()} - ${team.name}</A></LI>
   % endfor
</UL>