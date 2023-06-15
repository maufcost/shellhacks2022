from unittest import TextTestRunner
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_cors import CORS, cross_origin
import requests
import datetime
import json
import dotenv
import os
import re

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Load environment variables
dotenv.load_dotenv()
IPFS_KEY = os.getenv("IPFS_KEY", None)

def getVulnSeverity(numLines: int, numVulns: int) -> int:
	if numVulns == 0:
		return numVulns

	if numVulns <= numLines // 500:
		return 1

	return 2

def scan_code(code: str, ruleFiles: list([str])) -> tuple:
	vulns = []
	for ruleFile in ruleFiles:
		rule, info = parse_rule_file(ruleFile)
		if b'<<' in rule.encode():
			regexRes = re.match(r'(.*)<<(.*)>>', rule.encode())
			rule = regexRes.group(1)
			ruleParams = regexRes.group(2)
		paramsEval = True
		ruleRes = re.search(rule, code)
		try:
			charactersToHighlight=ruleRes.span()
			if paramsEval:
				vulnInfo = [info, charactersToHighlight]
				vulns.append(vulnInfo)
		except:
			pass
	vulnDisplay = []
	fileLines = code.encode().split(b'\n')
	for i in range(len(vulns)):
		chars = vulns[i][1]
		numNewLinesStart = code.encode()[:chars[0]].count(b'\n') + 1
		numNewLinesEnd = code.encode()[:chars[1]].count(b'\n') + 1
		vulns[i][1] = [numNewLinesStart, numNewLinesEnd]

	return vulns, getVulnSeverity(len(fileLines), len(vulns))

'''
Takes the url to an ipfs code object and return the entire code
'''
def parse_ipfs_code_from(code: str) -> str:
    if not code.startswith("ipfs://"):
        raise Exception("Invalid IPFS URL")
    code = code.replace("ipfs://", "https://ipfs.io/ipfs/")
    response = requests.get(code)
    if response.status_code != 200:
        raise Exception(response.text)
    return response.text

'''
Takes the url to an ipfs rule object and return the entire regex rule
'''
def parse_ipfs_rule_details(url_for_rule: str) -> str:
    if url_for_rule.startswith("ipfs://"):
        url_for_rule = url_for_rule.replace("ipfs://", "https://ipfs.io/ipfs/")
    if not url_for_rule.startswith("https://ipfs.io/ipfs/"):
        raise Exception("Invalid IPFS URL")
    response = requests.get(url_for_rule)
    if response.status_code != 200:
        raise Exception(response.text)
    return response.text

'''
Takes the url to an ipfs metadata object and return the entire metadata
'''
def parse_ipfs_url_data(url: str) -> dict:
    if url.startswith("ipfs://"):
        url = url.replace("ipfs://", "https://ipfs.io/ipfs/")
    if not url.startswith("https://ipfs.io/ipfs/"):
        raise Exception("Invalid IPFS URL")
    response = requests.get(url).json()
    return response

'''
Takes the url to an ipfs metadata object, gets the rule from, and returns the entire metadata
including the regex rule
'''
def parse_all_ipfs_data(metadata_url: str) -> dict:
    metadata = parse_ipfs_url_data(metadata_url)
    rule = parse_ipfs_rule_details((metadata["rule"])).replace("\r", "")    
    rule, info = parse_rule_file(str(rule))
    metadata["rule"] = rule
    return metadata

'''
Parses .rg file and splits it into the rule and info sections
'''
def parse_rule_file(contents: str) -> list([str, str]):
    res = re.search(r'% Rule\n+(.*)\n+% Info\n+([\s+\S+]+)', str(contents).replace("\r", ""))
    return [res.group(1), res.group(2)]

'''
Makes sure valid regex is uploaded so website doesn't break
'''
def check_regex_validity(regex: str) -> bool:
    try:
        re.compile(regex)
    except re.error:
        return False
    return True

'''
Parses .rg file from local directory or from web and uploads to IPFS
after checking if it's valid and safe.
'''
def parse_rg_file(rg_file: str, web: bool) -> list([str, str]):
    rule, info = ["", ""]
    if not web and (not rg_file or not rg_file.endswith(".rg")):
        raise Exception("File is not a .rg file")
    
    if not web:
        with open(rg_file, "r") as f:
            contents = f.read()
        rule, info = parse_rule_file(contents)
    else:
        rule, info = parse_rule_file(rg_file)
    
    if not rule or not info:
        raise Exception("Invalid formatting in .rg file")
    if not check_regex_validity(rule):
        raise Exception("Invalid regex in .rg file")
    return rule, info

# {'ok': True, 'value': {'ipnft': 'bafyreigjo7fx4aue7uxsnytuaavpznrpgvsbkdksppznne6gsnjf5bam34', 'url': 'ipfs://bafyreigjo7fx4aue7uxsnytuaavpznrpgvsbkdksppznne6gsnjf5bam34/metadata.json', 'data': {'name': 'test-rule-nobreak.rg', 'rule': 'ipfs://bafybeiewemksdxscjv7olvpw6bab2tycprgbpevvfctlwgfiyit3kmtsty/test-rule-nobreak.rg', 'info': ['https://cwe.mitre.org/data/definitions/94.html']}}} 
'''
Uploads a security regex rule to IPFS if all conditions are satisfied.
Returns the dictionary response from IPFS.
'''
def upload_rule_to_ipfs(rg_file: str, obj_metadata: dict, web: bool) -> dict:
    fields = [] # options for us: "name", "description", "tags", "category", "image", "image_url"
    if IPFS_KEY is None:
        raise Exception("IPFS_KEY not set")

    # Check if obj_metadata contains all fields
    if not all(field in obj_metadata for field in fields):
        raise Exception("obj_metadata missing fields")
    
    # Check if file is a valid .rg file
    try:
        rule, info = parse_rg_file(rg_file.decode('utf-8'), web)
        obj_metadata["rule"] = rule
        obj_metadata["info"] = info.split("\n")
        print(obj_metadata)
        url = "https://api.nft.storage/store"
        payload = {'meta': json.dumps(obj_metadata)}

        if web:
            files = [('rule', (obj_metadata["name"], rg_file, 'text/plain'))]
        else:
            files = [('rule', (obj_metadata["name"], open(rg_file, "rb"), "text/plain"))]

        headers = {
            'Authorization': f'Bearer {IPFS_KEY}',
            'accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        if response.status_code != 200:
            raise Exception(response.text)
        return response.json()
    except Exception as e:
        raise e

'''
Upload a code file to ipfs and return the ipfs data.
'''
def upload_code_to_ipfs(code_bytes: bytes, obj_metadata: dict) -> dict:
    fields = [] # options for us: "name", "description", "tags", "category", "image", "image_url"
    if IPFS_KEY is None:
        raise Exception("IPFS_KEY not set")

    # Check if obj_metadata contains all fields
    if not all(field in obj_metadata for field in fields):
        raise Exception("obj_metadata missing fields")
    
    try:
        url = "https://api.nft.storage/store"
        payload = {'meta': json.dumps(obj_metadata)}

        files = [('code', (obj_metadata["name"], code_bytes, 'text/plain'))]

        headers = {
            'Authorization': f'Bearer {IPFS_KEY}',
            'accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        if response.status_code != 200:
            raise Exception(response.text)
        return response.json()
    except Exception as e:
        raise e

# Route to upload a regex rule to IPFS
@cross_origin()
@app.route("/upload-rule", methods=["POST"])
def upload_rule():
    name = request.form.get("name")
    file_from_form = request.files['files[]']

    if name is None:
        name = file_from_form.filename

    return upload_rule_to_ipfs(file_from_form.read(), {"name": name, "rule":"undefined"}, True)

# Route to upload code files to IPFS
@cross_origin()
@app.route("/upload-code", methods=["POST"])
def upload_code():
    lang_map = {
        "py": "Python",
        "js": "JavaScript",
        "c": "C",
        "ts": "TypeScript",
        "go": "Go",
        "java": "Java",
        "rb": "Ruby",
        "rs": "Rust",
        "php": "PHP",
    }
    name = request.form.get("name")
    file_from_form = request.files['files[]']

    if name is None:
        name = file_from_form.filename
    
    # define programming language from file extension
    end = file_from_form.filename.split(".")[-1]
    lang = lang_map.get(end, "Unknown")

    return upload_code_to_ipfs(file_from_form.read(), {"name": name, "language": lang}), 200

@cross_origin()
@app.route("/code-analysis", methods=["POST"])
def code_analysis():
    list_of_rules = []
    code = parse_ipfs_code_from("ipfs://bafybeihyjwvvgmumyzpiqsmt5cgyiycadhqp4t2yohzgij3tedw7hqne2q/vulnerable.c").replace("\r", "")
    print(code)
    metadata = parse_ipfs_url_data("ipfs://bafyreidw3ffsqpdwklnmzlcuzwufdktic4cs5lvfbsfpwv3knqodxs3l34/metadata.json")
    print(metadata)
    rule = parse_ipfs_rule_details((metadata["rule"])).replace("\r", "")
    list_of_rules.append(rule)
    return jsonify(scan_code(code, list_of_rules)), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
