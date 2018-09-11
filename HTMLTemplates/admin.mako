<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Admin</%def>
<%inherit file="base.html"/>
<IMG ALT="TFI Logo" SRC="static/TFI-logo-smaller.png" WIDTH="250"/>

<H1>Admin Page</H1>

<br/>
<form action="addMember">
  <fieldset>
    <legend>Add a Member</legend>
    <table>
      <tr><td>Display Name:</td>
          <td><input autofocus type="text" name="display" placeholder="Member L"></td></tr>
      <tr><td>Barcode:</td>
          <td><input type="text" name="barcode" placeholder="123456"></td></tr>
    </table>
    <input type="submit" value="Add Member"/>
  </fieldset>
</form>

<form action="oops">
   <fieldset>
     <legend>Oops</legend>
   Keyholder accidentally signed out.  Move all FORGOT for today back to in.<br/>
  <input type="submit" value="Oops!"/>
</fieldset>
</form>

<H2>Fix "forgot" data</H2>
%if len(forgotDates):
  <FORM action="fixData">
  <SELECT id="date-select" name="date">
%for date in forgotDates:
    <OPTION value="${date}">${date}</OPTION>
%endfor
  </SELECT>
  <input type="submit" value="Fix Data"/>
</form>
%else:
  <P>Wow!  No dates that haven't been cleaned up!!</P>
%endif



<H2>Generate reports</H2>
<form action="reports" width="50%">
   <fieldset>
       <legend>Select Dates</legend>
   <div>
      <label for="start_date">Start Date:</label>
      <input id="start_date" type="date" name="startDate" value="${todayDate}"
       min="${firstDate}" max="${todayDate}"/>
   </div>
   <div>
      <label for="end_date">End Date:</label>
      <input id="end_date" type="date" name="endDate" value="${todayDate}"
       min="${firstDate}" max="${todayDate}"/>
   </div>

   <input type="submit" value="Generate Report"/>
   </fieldset>
</form>
<br/>
<FORM action="customSQLReport">
     <fieldset>
        <legend>For the <em>Real</em> Geek</legend>
     <textarea name="sql" rows="10" cols="80">
SELECT start, leave, displayName
FROM visits
INNER JOIN members ON members.barcode = visits.barcode
WHERE (start BETWEEN '2018-07-01' AND '2018-07-10');
     </textarea>
   <br/>
   <input type="submit" value="Generate Custom SQL Report"/>
 </fieldset>
</FORM>
