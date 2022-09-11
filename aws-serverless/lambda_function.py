import json
import base64
import re
import requests
import os
import pymongo

IPFS_KEY = os.environ['IPFS_KEY']
MONGO_KEY = os.environ['MONGO_KEY'] # Only for indexing ifps links
db_client = pymongo.MongoClient(f"mongodb+srv://midpoint:{MONGO_KEY}@cluster0.fbsnlnc.mongodb.net/?retryWrites=true&w=majority")

# Add a new rule metadata *ipfs link* to the database
def add_ipfs_rule_to_db(ipfs_metadata_url):
    db = db_client["pegasus"]
    collection = db["cyber-rules"]
    if collection.find_one({"rule_meta": ipfs_metadata_url}):
        return False
    collection.insert_one({"rule_meta": ipfs_metadata_url})
    return True

# get all ipfs links from the database
def get_all_rules():
    db = db_client["pegasus"]
    collection = db["cyber-rules"]
    all_rules = collection.find({})
    all_rules = [rule['rule_meta'] for rule in all_rules]
    return all_rules


def parse_rule_file(contents: str) -> list([str, str]):
    res = re.search(r'% Rule\n+(.*)\n+% Info\n+([\s+\S+]+)', str(contents).replace("\r", ""))
    return [res.group(1), res.group(2)]

def check_regex_validity(regex: str) -> bool:
    try:
        re.compile(regex)
    except re.error:
        return False
    return True

def parse_ipfs_rule_details(url_for_rule: str) -> str:
    if url_for_rule.startswith("ipfs://"):
        url_for_rule = url_for_rule.replace("ipfs://", "https://ipfs.io/ipfs/")
    if not url_for_rule.startswith("https://ipfs.io/ipfs/"):
        raise Exception("Invalid IPFS URL")
    response = requests.get(url_for_rule)
    if response.status_code != 200:
        raise Exception(response.text)
    return response.text

def parse_ipfs_code_from(code: str) -> str:
    if not code.startswith("ipfs://"):
        raise Exception("Invalid IPFS URL")
    code = code.replace("ipfs://", "https://ipfs.io/ipfs/")
    response = requests.get(code)
    if response.status_code != 200:
        raise Exception(response.text)
    return response.text

def parse_rg_file(rg_file: str) -> list([str, str]):
    rule, info = parse_rule_file(rg_file)
    if not rule or not info:
        raise Exception("Invalid formatting in .rg file")
    if not check_regex_validity(rule):
        raise Exception("Invalid regex in .rg file")
    return rule, info

def parse_ipfs_url_data(url: str) -> dict:
    if url.startswith("ipfs://"):
        url = url.replace("ipfs://", "https://ipfs.io/ipfs/")
    if not url.startswith("https://ipfs.io/ipfs/"):
        raise Exception("Invalid IPFS URL")
    response = requests.get(url).json()
    return response

def upload_rule_to_ipfs(rg_file: str, obj_metadata: dict) -> dict:
    if IPFS_KEY is None:
        raise Exception("IPFS_KEY not set")
    try:
        rule, info = parse_rg_file(rg_file.decode('utf-8'))
        obj_metadata["rule"] = rule
        obj_metadata["info"] = info.split("\n")
        obj_metadata["name"] = obj_metadata["info"][-1]
        print(obj_metadata)
        url = "https://api.nft.storage/store"
        payload = {'meta': json.dumps(obj_metadata)}
        files = [('rule', ("pegasus_rule", rg_file, 'text/plain'))]
        headers = {
            'Authorization': f'Bearer {IPFS_KEY}',
            'accept': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print(response)
        if response.status_code != 200:
            raise Exception(response.text)
        return response.json()
    except Exception as e:
        raise e

def upload_code_to_ipfs(code_bytes: bytes, obj_metadata: dict) -> dict:
    if IPFS_KEY is None:
        raise Exception("IPFS_KEY not set")
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

def getVulnSeverity(numLines: int, numVulns: int) -> int:
	if numVulns == 0:
		return numVulns

	if numVulns <= numLines // 500:
		return 1

	return 2

def scan_code(code: str, ruleFiles: list([str])) -> tuple:
    vulns = []
    for ruleFile in ruleFiles:
        if type(ruleFile) == tuple:
            rule, info = ruleFile
        else:
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

def lambda_handler(event, context):
    # If the request is a POS to /upload-rule, then upload the rule to IPFS
    if event.get("requestContext").get('http').get("method") == 'POST' and event.get("requestContext").get('http').get("path") == '/upload-rule':
        # Get the rule from the body
        rule = event.get("body")
        decoded_rule = base64.b64decode(rule)
        res = upload_rule_to_ipfs(decoded_rule, {"name":"name", "rule":"undefined"})
        add_ipfs_rule_to_db(res["value"]["url"])
        return {
            'statusCode': 200,
            'body': json.dumps(res)
        }
    
    if event.get("requestContext").get('http').get("method") == 'POST' and event.get("requestContext").get('http').get("path") == '/upload-code':
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

        code = event.get("body")
        decoded_code = base64.b64decode(code)
        code_res = upload_code_to_ipfs(decoded_code, {"name":"pegasus-code"})
        return {
            'statusCode': 200,
            'body': json.dumps(code_res)
        }
    
    if event.get("requestContext").get('http').get("method") == 'POST' and event.get("requestContext").get('http').get("path") == '/code-analysis':
        buff = "(\w+)\s?\[(\d+)\].*[\s+\S+]+(fgets\s?\(\s?\1\s?,\s?(\d+)\s?,.*\))".replace("\r", "")
        buff_info = "Stack-Based Buffer Overflow Resulting from function fgets() reading into buffer of insufficient size\nhttps://cwe.mitre.org/data/definitions/121.html"
        body = event.get("body")
        list_of_rules = []
        body = json.loads(body)
        code = body.get('code')
        code = parse_ipfs_code_from(code).replace("\r", "")
        # stale = body.get('rules')
        # print(code)

        # list_of_metadatas = get_all_rules()
        # for each_meta in list_of_metadatas:
        #     metadata = parse_ipfs_url_data(each_meta)
        #     print(metadata)
        #     rule = parse_ipfs_rule_details((metadata["rule"])).replace("\r", "")
        #     list_of_rules.append(rule)

        scan_res = scan_code(code, [(buff, buff_info)])

        return {
            'statusCode': 200,
            'body': json.dumps({"scan_res": scan_res})
        }

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }