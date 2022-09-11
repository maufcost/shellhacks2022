% Rule
{{.*\w*(?<!render_template_string).*\b(?:input|request\.form).*}}|{%.*\w*(?<!render_template_string).*\b(?:input|request\.form).*%}
% Info
Server-Side Template Injection (SSTI) by including unsanitized input in a rendered template. 
https://cwe.mitre.org/data/definitions/1336.html
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8341
