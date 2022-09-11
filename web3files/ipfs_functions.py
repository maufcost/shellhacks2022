from msilib.schema import File
from wsgiref import headers
import requests
import datetime
import json
import dotenv
import os
import re

# Load environment variables
dotenv.load_dotenv()
IPFS_KEY = os.getenv("IPFS_KEY", None)

def parse_rule_file(contents: str) -> list([str, str]):
	res = re.search(r'% Rule\n+(.*)\n+% Info\n+([\s+\S+]+)', contents)
	return [res.group(1), res.group(2)]

def check_regex_validity(regex: str) -> bool:
    try:
        re.compile(regex)
    except re.error:
        return False
    return True

def parse_rg_file(rg_file: str) -> list([str, str]):
    if not rg_file or not rg_file.endswith(".rg"):
        raise Exception("File is not a .rg file")
    with open(rg_file, "r") as f:
        contents = f.read()
    rule, info = parse_rule_file(contents)
    if not rule or not info:
        raise Exception("Invalid formatting in .rg file")
    if not check_regex_validity(rule):
        raise Exception("Invalid regex in .rg file")
    return rule, info

def upload_rule_to_ipfs(rg_file: str, obj_metadata: dict) -> str:
    fields = [] # options for us: "name", "description", "tags", "category", "image", "image_url"
    if IPFS_KEY is None:
        raise Exception("IPFS_KEY not set")

    # Check if obj_metadata contains all fields
    if not all(field in obj_metadata for field in fields):
        raise Exception("obj_metadata missing fields")
    
    # Check if file is a valid .rg file
    try:
        rule, info = parse_rg_file(rg_file)
        obj_metadata["rule"] = rule
        obj_metadata["info"] = info

        url = "https://api.nft.storage/store"
        payload = {'meta': json.dumps(obj_metadata)}
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

print(upload_rule_to_ipfs("test.rg", {"name": "Test Rule", "rule": "undefined"}))