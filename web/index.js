const express = require('express')
const fs = require('fs');
var spawn = require("child_process").spawn;
var bodyParser = require('body-parser');


const app = express()
const port = 8000

app.use( bodyParser.json() );
app.use(bodyParser.urlencoded({
  extended: true
})); 

app.get('/form', (req, res) => {
  fs.readFile("./formulaire.html", function (error, html) {
    if (error) {
      throw error;
    }
    res.end(html);
  });
})

app.post('/rep', (req,res) => {
  var Args = ["../main.py", "process"];
  Args.push("rgb");
  if (req.body.red && req.body.green && req.body.blue) {
    Args.push(req.body.red);
    Args.push(req.body.green);
    Args.push(req.body.blue);
  }
  Args.push("shape");
  if (Array.isArray(req.body.shape)) {
    req.body.shape.forEach((shape) => {
      Args.push(shape);
    });
  } else {
    if (req.body.shape) {
      Args.push(req.body.shape);
    }
    
  }
  Args.push("surface");
  if (Array.isArray(req.body.surface)) {
    req.body.surface.forEach((surface) => {
      Args.push(surface);
    });
  } else {
    if (req.body.surface) {
      Args.push(req.body.surface);
    }
  }
  Args.push("model");
  Args.push(req.body.model);

  var process = spawn('python3',Args);
  process.stdout.on('data', (data) => {
    console.log(data.toString('utf8'));
    res.send(data.toString('utf8'));
  });

  process.stderr.on('data', (stacktrace) => {
    console.error(stacktrace.toString('utf8'));
  });

  process.on('exit', (exitCode) => {
    console.log(`Process ended with code (${exitCode})`);
  });
})

app.listen(port, () => {
  console.log(`Listening on port ${port}`)
})