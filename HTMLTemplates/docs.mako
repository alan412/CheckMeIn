<%def name="scripts()">
</%def>
<%def name="head()">
</%def>

<%def name="title()">CheckMeIn Admin</%def>
<%inherit file="base.mako"/>
${self.logo()}<br/>
<H2>Documentation</H2>
<P>
Most of CheckMeIn is designed to be used through the webapp only.   However, there are a few defined endpoints for other systems to interact.

% for doc in docs:
<details>
  <summary>${doc.summary}</summary>
  <pre><code>${doc.code}</code></pre>
  <UL>
  % for note in doc.notes:
  <LI>${note}</LI>
  % endfor
  </UL>
  <p><b>Returns:</b> ${doc.returns}</p>
</details>
% endfor

<hr/>
To add feature requests or report issues, please go to:<A HREF="https://github.com/alan412/CheckMeIn/issues">https://github.com/alan412/CheckMeIn/issues</A>