require 'json'
require 'tempfile'

my_html = "<html><head><body><h2>This is wrong, it should be h1"

tmp_file = Tempfile.new()
tmp_file.write(my_html)
tmp_file.close

results = `zookeeper tarsier #{tmp_file.path} -J`
json_results = JSON.parse(results)
print json_results[0][0], " ", json_results[0][1]['failures'].size, " failures\n"
