const express = require('express')
const fs = require('fs');
var spawn = require("child_process").spawn;
const app = express()
const port = 8000

app.get('/form', (req, res) => {
  fs.readFile("./formulaire.html", function (error, html) {
    if (error) {
      throw error;
    }
    res.end(html);
  });
})

app.post('/rep', (req,res) => {
    
    var process = spawn('python',["../process.py"]);
    process.stdout.on('data', (data) => {
        console.log(data.toString('utf8'));
    });

    process.stderr.on('data', (stacktrace) => {
        console.error(stacktrace.toString('utf8'));

        // possibly parse the stack trace to handle distinct exceptions
    });

    process.on('exit', (exitCode) => {
        console.log(`Process ended with code (${exitCode})`);
    });
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})