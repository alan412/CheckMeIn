<%def name="scripts()">
<script>
window.onload = setTimeout(function(){location.href="/station"},1000*60);  // every minute
</script>
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Station</%def>
<%inherit file="base.mako"/>
<TABLE>
<TR><TD WIDTH="20%">
${self.logo()}<br/>
<div id="member_id">
<form action="/station/scanned">
     <input id="member_id" type="text" name="barcode" size="8" autofocus placeholder="Member ID"/><br/>
</form>
</div>
</TD>
<TD WIDTH="60%">
     <CENTER><H1>Welcome to TFI Headquarters</H1>
     <H2><div id="clockbox"></div></H2>
</TD>
    <TD class="who_is_here" valign=center><CENTER><P>To see who is here:</P>
<A HREF="http://tfi.ev3hub.com/"><IMG ALT="qr-code" WIDTH="100" SRC="/static/qrcode-who_is_here.png"/></A>
<br/>
<A HREF="http://tfi.ev3hub.com">http://tfi.ev3hub.com</A>
<center/>
</TD>

</TR></TABLE>

<table class="recent" style="width:100%">
<TR>
<TD style="width:70%" valign="top">
  <H2>Recent Activity (today)</H2>
  <TABLE style="width:80%">
    <TR><TH>Time</TH><TH>Name</TH><TH>Description</TH></TR>
  % for trans in todaysTransactions:
    <TR class="${trans.description}"><TD>${trans.time.strftime("%I:%M %p")}</TD><TD>${trans.name}</TD><TD>${trans.description}</TD></TR>
  % endfor
  </TABLE>
</TD>
<TD style="width:30%" valign="top">
<table class="side">
  <TR>
    <TH># people in building</TH>
    <TD>${numberPresent}</TD>
  </TR>
  <TR>
    <TH>Total people today</TH>
    <TD>${uniqueVisitorsToday}</TD>
  </TR>
  <TR>
    <TH>Keyholder</TH>
    <TD>${keyholder_name}</TD>
  </TR>
  </table>
</TD>
</TR>
</table>

<script type="text/javascript">
tday=new Array("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday");
tmonth=new Array("January","February","March","April","May","June","July","August","September","October","November","December");

function GetClock(){
var d=new Date();
var nday=d.getDay(),nmonth=d.getMonth(),ndate=d.getDate(),nyear=d.getFullYear();
var nhour=d.getHours(),nmin=d.getMinutes(),nsec=d.getSeconds(),ap;

if(nhour==0){ap=" AM";nhour=12;}
else if(nhour<12){ap=" AM";}
else if(nhour==12){ap=" PM";}
else if(nhour>12){ap=" PM";nhour-=12;}

if(nmin<=9) nmin="0"+nmin;
if(nsec<=9) nsec="0"+nsec;

document.getElementById('clockbox').innerHTML=""+tday[nday]+", "+tmonth[nmonth]+" "+ndate+", "+nyear+"<br/>"+nhour+":"+nmin+":"+nsec+ap+"";
}

window.onload=function(){
GetClock();
setInterval(GetClock,1000);
}
</script>
