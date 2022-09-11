% Rule
\b(?:system|popen|Popen|open|subprocess\.call|subprocess\.Popen|eval)\b\s?\(\s?\b(?:input\(.*\))\s?|\.?get\s?\(\w+\)\)

% Info
Code Injection Vulnerability by executing unsanitized input
https://cwe.mitre.org/data/definitions/94.html
https://capec.mitre.org/data/definitions/242.html

