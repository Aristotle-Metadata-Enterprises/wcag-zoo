#!/usr/bin/env ruby
require 'json'
require 'tempfile'

my_html = "<html><head><body><h1>1</h1><h3>This is wrong, it should be h2"

tmp_file = Tempfile.new('foo')
tmp_file.write(my_html)
tmp_file.close

results = `zookeeper tarsier #{tmp_file.path} -F`
json_results = JSON.parse(results)
print json_results[0][0], " ", json_results[0][1]['failures'].size, " failures\n"
