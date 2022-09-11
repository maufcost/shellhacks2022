#!/bin/python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
from pathlib import Path


# For use of API
app = Flask(__name__)
CORS(app)



'''
For internal use only

This takes the contents of the *.rg file and returns as a tuple:

Index 0:
The rule in custom regex

Index 1:
The information on the vulnerability (eg. mitre links and recommendations)


'''
def parse_rule_file(contents: str) -> list[str, str]:
	res = re.search(rb'% Rule\n+(.*)\n+% Info\n+([\s+\S+]+)', contents)
	return [res.group(1), res.group(2)]


'''
Returns severity: 0, 1, 2
This can be interpreted as: Excellent, Good, Bad

Uses an arbitrary metric of: Every 500 lines of code may have a vulnerability
'''
def getVulnSeverity(numLines: int, numVulns: int) -> int:
	if numVulns == 0:
		return numVulns

	if numVulns <= numLines // 500:
		return 1

	return 2

'''
Check all rules against the code.

'''
def scan_code(code: str, ruleFiles: list[str]) -> tuple:
	vulns = []

	# Check how many vulnerabilities

	for ruleFile in ruleFiles:
		rule, info = parse_rule_file(ruleFile)
		# print(rule, info)
		if b'<<' in rule:
			regexRes = re.match(r'(.*)<<(.*)>>', rule)
			rule = regexRes.group(1)
			ruleParams = regexRes.group(2)


		# TODO: Perform eval for complex rules.
		# Possibly use python parse library
		# paramsEval = eval()
		paramsEval = True

		ruleRes = re.search(rule, code)
		try:
			charactersToHighlight=ruleRes.span() # tuple with start to end char
			
			# If we match and necessary parameters are met to indicate a vulnerability,
			# then add to the vulnerability list
			if paramsEval:
				vulnInfo = [info, charactersToHighlight]
				vulns.append(vulnInfo)
		except:
			pass


	# Parse initial vulnerability analysis 

	
	## TODO: Change from highlighting characters to highlighting lines

	# vulnDisplay = []
	fileLines = code.split(b'\n')

	return vulns, getVulnSeverity(len(fileLines), len(vulns))

'''
potential api for scanning code. 

this technically could be considered slightly insecure bc
we would be storing the "secure decentralized" data in memory.
probs not that big of a problem though.

'''
@app.route("/scan-code", methods=['POST'])
def scanner_api():
	
	# this needs to be modified based on how the request 
	# is going to be made
	inpData = request.get_json(force=True)



	return jsonify(scan_code(inpData)), 200, {'ContentType':'application/json'}



	

# Read in all the files

codePath = './example_code/buf1.c'
rulesPath = './example_rules' # this should be changed to './rules if running locally'

rules = []

## TODO: Make this decentralized

# Read in rules from local directory
for path in Path(rulesPath).rglob('*.rg'):
	with open(path, 'rb') as fin:
		rules.append(fin.read().rstrip())

with open(codePath, 'rb') as fin:
	code = fin.read().rstrip()

print(scan_code(code, rules))

# Scan code with the file







