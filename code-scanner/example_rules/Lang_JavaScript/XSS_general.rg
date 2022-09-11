% Rule
.*\w*(?<!X-XSS-Protection).*\b(?:eval|request\.get|form\.get).*[\s+\S+]+
% Info
Cross-Site Scripting Vulnerability (XSS) As a result of no input sanitization
https://cwe.mitre.org/data/definitions/79.html
