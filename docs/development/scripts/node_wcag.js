#!/usr/bin/env node
var temp = require('temp'),
    fs   = require('fs'),
    exec = require('child_process').exec;

temp.open('wcag', function(err, info) {
  if (!err) {
    fs.write(
      info.fd,
      "<html><head><body><h1>Heading 1</h1><h3>This is wrong, it should be h2",
      function(err){
        /* Ignore, we don't care */
      }
    );
    fs.close(info.fd, function(err) {
      exec("zookeeper tarsier '" + info.path + "' -F",
        function(err, stdout) {
          results = stdout;
          json_results = JSON.parse(results);
          console.log(
            json_results[0][0],
            json_results[0][1].failures.length,
            "failures"
          );
        }
      );
    });
  }
});
