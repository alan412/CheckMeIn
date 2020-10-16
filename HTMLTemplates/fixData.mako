<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Fix Data</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H1>Fix Data Page for ${date}</H1>
<TABLE>
  <TR><TH>Display Name</TH><TH>Start</TH><TH>Leave</TH><TH>Update</TH></TR>
% for row in data:
  <TR class="dataRow ${row.status}" id="Fix-${row.rowid}"><TD>${row.name}</TD>
    <TD class="start">
      <input class="hour" type="number" min="1" max="12" value=
    "${ row.start.hour if (row.start.hour < 13) else row.start.hour - 12}" onchange="itemChanged(this);">:
        <input class="minute" type="number" min="0" max="60" value="${row.start.minute}" onchange="itemChanged(this);">
        <select class="period" onchange="itemChanged(this);">
           <option value="AM" ${"selected" if (row.start.hour < 12) else ""}>AM</option>
           <option value="PM" ${"selected" if (row.start.hour > 11) else ""}>PM</option>
        </select>
    </TD>
    <TD class="leave"><input class="hour" type="number" min="1" max="12" value=
    "${ row.leave.hour if (row.leave.hour < 13) else row.leave.hour - 12}" onchange="itemChanged(this);">:
        <input class="minute" type="number" min="0" max="60" value="${row.leave.minute}" onchange="itemChanged(this);">
        <select class="period" onchange="itemChanged(this);"><option value="AM" ${"selected" if (row.leave.hour < 12) else ""}>AM</option>
                <option value="PM" ${"selected" if (row.leave.hour > 11) else ""}>PM</option>
        </select>
    </TD>
    <TD><CENTER><input class="updateCheck" type="checkbox"/></CENTER></TD>
  </TR>
% endfor
</TABLE>
<form id="formID" action="fixed">
   <input id="output" hidden name="output" type="textarea"/><br/> <!-- This is just for debugging! -->
   <input type="button" value="Submit" onclick="submitPressed()")/>
</form>

<script>
function itemChanged(item){
    $( '.updateCheck', item.closest('tr')).prop("checked", true);
}

function returnTime(el){
    return '${date} ' + $('.hour', el).val() + ':' +
           $('.minute', el).val() + $('.period', el).val();
}

function submitPressed(){
    var dataItems = $( '.dataRow' );
    var dataString = "";
    $( '.dataRow' ).each(function( index, elem ) {
      var update = $( '.updateCheck', this).prop('checked');
      if(update){
         dataString += this.id.substring(4) + '!' + returnTime($('.start', this)) + '!' +
                                       returnTime($('.leave', this)) + ',';
      }
  // this: the current, raw DOM element
  // index: the current element's index in the selection
  // elem: the current, raw DOM element (same as this)
});
  $( '#output').val(dataString);
  $("form#formID").submit();
}
</script>
