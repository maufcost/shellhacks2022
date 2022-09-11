% Rule
.*\w*(?<!render_template_string)\.execute\s?\(\b(?:input|request\.form).*
% Info
SQL Injection Vulnerability as a result of querying with unsanitized user input
https://cwe.mitre.org/data/definitions/89.html
https://attack.mitre.org/techniques/T1190/
