<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Report</%def>
<%inherit file="base.mako"/>
<CENTER>
<IMG ALT="TFI Logo" SRC="static/TFI-logo-smaller.png" WIDTH="250"/>
</CENTER>

% if stats.beginDate == stats.endDate:
   <H1>Report for ${stats.beginDate}</H1>
% else:
   <H1>Report for ${stats.beginDate} to ${stats.endDate}</H1>
% endif

<H2>Statistics</H2>
<UL>
  <LI>Number of unique visitors: ${stats.uniqueVisitors}</LI>
  <LI>Total number of hours spent: ${'% 6.1f' % stats.totalHours}</LI>
  <LI>Average time per visitor: ${'% 6.1f' % stats.avgTime}</LI>
  <LI>Median time per visitor: ${'% 6.1f' % stats.medianTime}</LI>
  <LI>Top 10 by time spent</LI><TABLE>
      % for person in stats.top10:
         <TR><TD>${person.name}</TD><TD>${'% 6.1f' % person.hours}</TD></TR>
      % endfor
      </TABLE>
  </UL>
</UL>
<H2>Graph by day</H2>
<P>Coming soon!</P>

<H2>Graph building usage by day/time</H2>
<P>Coming soon!</P>

<H2>Full List</H2>
<TABLE>
    % for person in stats.sortedList:
       <TR><TD>${person.name}</TD><TD>${'% 6.1f' % person.hours}</TD></TR>
    % endfor
</TABLE>
