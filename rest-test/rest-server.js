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

var namespace_obj = { }


app.route('/api/share/:namespace/:building?').get(function(req, res){
    console.log("get SHARE")

    if (!(req.params.namespace in namespace_obj))
    {
        namespace_obj[req.params.namespace] = {}
    }

    res.json(namespace_obj[req.params.namespace])
});

app.route('/api/share/:namespace/:building?').post(function(req, res){
    console.log("POST SHARE")
    if (!(req.params.namespace in namespace_obj))
    {
        namespace_obj[req.params.namespace] = {}
    }

    if (req.params.building_id != undefined)
        namespace_obj[req.params.namespace][req.params.building_id][req.body.variable_name] = {
            "value":req.body.value,
            "timestamp": new Date().getTime()
        }
    else
        namespace_obj[req.params.namespace][req.body.variable_name] = {
            "value":req.body.value,
            "timestamp": new Date().getTime()
        }

    res.json({})
});

app.listen(port);