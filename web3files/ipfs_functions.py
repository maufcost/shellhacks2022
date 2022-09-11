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

def parse_ipfs_rule_details(url_for_rule: str) -> dict:
    if url_for_rule.startswith("ipfs://"):
        url_for_rule = url_for_rule.replace("ipfs://", "https://ipfs.io/ipfs/")
    if not url_for_rule.startswith("https://ipfs.io/ipfs/"):
        raise Exception("Invalid IPFS URL")
    response = requests.get(url_for_rule)
    if response.status_code != 200:
        raise Exception(response.text)
    return response.text

def parse_ipfs_url_data(url: str) -> dict:
    if url.startswith("ipfs://"):
        url = url.replace("ipfs://", "https://ipfs.io/ipfs/")
    if not url.startswith("https://ipfs.io/ipfs/"):
        raise Exception("Invalid IPFS URL")
    response = requests.get(url).json()
    return response

def parse_all_ipfs_data(metadata_url: str) -> dict:
    metadata = parse_ipfs_url_data(metadata_url)
    rule = parse_ipfs_rule_details((metadata["rule"])).replace("\r", "")    
    rule, info = parse_rule_file(str(rule))
    metadata["rule"] = rule
    return metadata

def parse_rule_file(contents: str) -> list([str, str]):
    res = re.search(r'% Rule\n+(.*)\n+% Info\n+([\s+\S+]+)', str(contents).replace("\r", ""))
    return [res.group(1), res.group(2)]

def check_regex_validity(regex: str) -> bool:
    try:
        re.compile(regex)
    except re.error:
        return False
    return True

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

@cross_origin()
@app.route("/upload", methods=["POST"])
def upload():
    name = request.form.get("name")
    file_from_form = request.files['files[]']

    if name is None:
        name = file_from_form.filename

    print(upload_rule_to_ipfs(file_from_form.read(), {"name": name, "rule":"undefined"}, True))
    return "OK", 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)