import json
import base64
import re
import requests
import os

IPFS_KEY = os.environ['IPFS_KEY']

def parse_rule_file(contents: str) -> list([str, str]):
    res = re.search(r'% Rule\n+(.*)\n+% Info\n+([\s+\S+]+)', str(contents).replace("\r", ""))
    return [res.group(1), res.group(2)]

def check_regex_validity(regex: str) -> bool:
    try:
        re.compile(regex)
    except re.error:
        return False
    return True

def parse_rg_file(rg_file: str) -> list([str, str]):
    rule, info = parse_rule_file(rg_file)
    if not rule or not info:
        raise Exception("Invalid formatting in .rg file")
    if not check_regex_validity(rule):
        raise Exception("Invalid regex in .rg file")
    return rule, info

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

def lambda_handler(event, context):
    # If the request is a POS to /upload-rule, then upload the rule to IPFS
    if event.get("requestContext").get('http').get("method") == 'POST' and event.get("requestContext").get('http').get("path") == '/upload-rule':
        # Get the rule from the body
        rule = event.get("body")
        decoded_rule = base64.b64decode(rule)
        res = upload_rule_to_ipfs(decoded_rule, {"name":"name", "rule":"undefined"})
        return {
            'statusCode': 200,
            'body': json.dumps(res)
        }

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }