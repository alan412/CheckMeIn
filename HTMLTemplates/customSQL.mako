<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Report - CustomSQL</%def>
<%inherit file="base.mako"/>
<CENTER>
<IMG ALT="TFI Logo" SRC="static/TFI-logo-smaller.png" WIDTH="250"/>
</CENTER>

%if report_title:
  <H1>${report_title}</H1>
%endif

<FORM action="customSQLReport">
     <fieldset>
        <legend>SQL command</legend>
     <textarea name="sql" rows="10" cols="80">
${sql}
     </textarea>
   <br/>
   <input type="submit" value="Generate Custom SQL Report"/>
 </fieldset>
</FORM>

<H2>Output</H2>
<table class="SQLoutput">
% for row in data:
<tr>
  % for datum in row:
     <td class="SQLoutput">${datum}</td>
  % endfor
</tr>
% endfor
</table>

<br/>
<FORM action="saveReport">
     <fieldset>
        <legend>Save Report</legend>
    <label for="report_name">Report Name:</label>
    <input type="text" size="40" name="report_name" placeholder="Friendly name here"/><br/>
   <br/>
   <input type="hidden" name="sql" value="${sql}"/>
   <input type="submit" value="Save Report"/>
 </fieldset>
</FORM>
