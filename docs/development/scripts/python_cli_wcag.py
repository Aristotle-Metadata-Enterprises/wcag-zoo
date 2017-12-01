#!/usr/bin/env python2
from __future__ import print_function
import json
import tempfile
import subprocess

my_html = "<html><head><body><h1>1</h1><h3>This is wrong, it should be h2"

tmp_file = tempfile.NamedTemporaryFile()
tmp_file.write(my_html)
tmp_file.seek(0)

process = subprocess.Popen(
    ["zookeeper", "tarsier", tmp_file.name, "-F"],
    stdout=subprocess.PIPE
)

results = process.communicate()[0]
json_results = json.loads(results)

print(json_results[0][0],
    len(json_results[0][1]['failures']),
    "failures"
)
