#!/bin/python3
import os
import json
import sys
import ipfshttpclient


base_addr = sys.argv[1: ]

client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')


