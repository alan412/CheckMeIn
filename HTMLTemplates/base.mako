<%def name="logo()"><IMG ALT="TFI Logo" SRC="/static/TFI-logo-smaller.png" WIDTH="250"/>
</%def>
## base.mako
<!DOCTYPE html>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
${self.scripts()}
<script>
function pythonDatetimeToHTML(datetime){
	var js_datetime = new Date(datetime * 1000);
	var options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName : 'short'};
	return js_datetime.toLocaleString("en-US", options);
}
function pythonDateToHTML(datetime){
	var js_datetime = new Date(datetime * 1000);
	var options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'};
	return js_datetime.toLocaleString("en-US", options);
}

function trimInput(control){
	control.value = $.trim(control.value);
}

$( document ).ready(function(){
	$(".date").each(function(){
		$( this ).text(pythonDatetimeToHTML($(this).text()));
	});
});
var entityMap = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': '&quot;',
  "'": '&#39;',
  "/": '&#x2F;'
};

function escapeHTML(string) {
  return String(string).replace(/[&<>"'\/]/g, function (s) {
    return entityMap[s];
  });
}
</script>
<html>
	<head>
		<link rel="stylesheet" type="text/css" href="/static/style.css"/>
	    <title>${self.title()}</title>
         ${self.head()}
         <meta name="viewport" content="width=device-width, initial-scale=1">
	</head>
    <body>
% if error is not UNDEFINED:
	    <H1 class="error" id="error">${error}</H1>
% endif
<div id="modal" class="modal">
	<div class="modal-content">
		<div class="modal-header">
		   <span class="close">&times;</span>
		   <h2 id="modal-header"></h2>
		</div>
		<div id="modal-body" class="modal-body">
			<p/>
		</div>
	</div>
</div>
        ${self.body()}
    </body>
</html>
