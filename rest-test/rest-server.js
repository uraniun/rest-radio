var express = require('express'),
  app = express(),
  port = 8000,
  bodyParser = require('body-parser');


app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.route('/api/rooms/:room').post(function(req, res){
    console.log(req.params)
    console.log(req.body)
    res.json({message:"success"})
});

app.listen(port);