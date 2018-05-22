import json, os, re

import ./utils

type_mapping = {
    "string":"ManagedString",
    "int": "int",
    "float": "float"
}

tab = "    "

def generate_return_type(returns,service_name, ep_name):

    ep_name = ep_name[0].upper() + ep_name[1:]

    if len(returns) > 1:
        struct = "struct " + service_name + ep_name + " {\r\n"

        for r in returns:
            struct += tab + type_mapping[r["type"]] + " " + r["name"] + ";\r\n"

        struct += "};\r\n"

        return {"type": service_name + ep_name, "struct": struct}

    if len(returns) == 0:
        return {"type":"int","struct":""}

    return { "type": type_mapping[returns[0]["type"]], "struct": ""}

def generate_function_body(parameters, microbit_query, endpoint, return_type, returns, request_type, cache_ms = 0):

    query_string = re.findall("(%([a-zA-z?]*)%)", microbit_query)

    parameters +=  [{
        "name": "endpoint",
        "value": endpoint,
        "type":"inline"
    }]

    body = ""

    query_string_param = []
    standard_param = []

    # for each parameter work out if it belongs in the query string
    # if it does not, add to standard parameter list
    # if it does add to query_string_param_list
    for p in parameters:
        standard = True
        for tup in query_string:
            full, variable_name = tup[0], tup[1]
            if p["name"] == variable_name:
                p["pattern"] = full
                query_string_param += [p]
                standard = False

        if standard:
            standard_param += [p]

    # at the end, if there are missing items from the query string param list that are in the query string, we mark to omit
    for tup in query_string:
        added = False
        for p in query_string_param:
            if tup[1] == p["name"]:
                added = True

        if not added:
            # if we didn't find a matching key for a pattern in the query string, mark to omit so it is removed from the url.
            query_string_param += [{
                "pattern":full,
                "omit":True
            }]

    if len(query_string_param) > 0:
        #generate url
        for q in query_string_param:
            print q
            if "omit" in q.keys():
                microbit_query = microbit_query.replace(q["pattern"], '')
            elif q["type"] == "inline":
                if q["value"] == "none":
                    microbit_query = microbit_query.replace(q["pattern"]+"/", '')
                else:
                    microbit_query = microbit_query.replace(q["pattern"], q["value"])
            else:
                microbit_query = microbit_query.replace(q["pattern"], "\" + " + q["name"] + " + \"")

    if len(standard_param) > 0:
        body += tab + "DynamicType t;\r\n"

        # generate packing of data
        for st in standard_param:
            param_type = st["type"]

            if param_type == "string":
                body += tab + 't.appendString('+st["name"]+");\r\n"
            elif param_type == "int":
                body += tab + 't.appendInteger('+st["name"]+");\r\n"
            elif param_type =="float":
                body += tab + 't.appendFloat('+st["name"]+");\r\n"

    #perform request
    if request_type == "GET":
        body += tab + "DynamicType res = radio.rest.getRequest(\"" + microbit_query +"\");\r\n"
    if request_type == "POST":
        body += tab + "DynamicType res = radio.rest.postRequest(\"" + microbit_query +"\", t);\r\n"

    if len(returns) == 0:
        body += tab + "return res.getStatus();\r\n"

    if len(returns) == 1:
        if return_type["type"] == "ManagedString":
            body += tab + 'return res.getString(0);\r\n'
        elif return_type["type"] == "int":
            body += tab + 'return res.getInteger(0);\r\n'
        elif return_type["type"] =="float":
            body += tab + 'return res.getFloat(0);\r\n'

    if len(returns) > 1:
        body += tab + return_type["type"] + " ret;\r\n"

        body += tab + "if (res.getStatus() == MICROBIT_OK) {\r\n"

        # generate unpacking
        for idx,r in enumerate(returns):
            param_type = r["type"]
            body += (2 * tab) + "ret." + r["name"]+ " = "

            if param_type == "string":
                body += 'res.getString('+str(idx)+");\r\n"
            elif param_type == "int":
                body += 'res.getInteger('+str(idx)+");\r\n"
            elif param_type =="float":
                body += 'res.getFloat('+str(idx)+");\r\n"

        body += tab + "}\r\n"

        body += tab + "return ret;\r\n"

    # if we would like to cache the result (to prevent thrashing)
    # if cache_ms > 0:
        #return function body with async caching behaviour
        #return idle body

    # generate unpacking of data into c struct

    #return function body with no caching, return blank idle body
    return body

def generate_function_definition(return_type, service_key_name, service_name, ep_name, parameters, microbit_query, returns, request_type, api_prefix):

    out = {}

    api_name = api_prefix + ep_name[0].upper() + ep_name[1:]

    h_definition = return_type["type"] + " " + api_name + "("

    cpp_definition = return_type["type"] + " " + service_name+"::" + api_name + "("

    try:
        param_list = ', '.join([type_mapping[p["type"]] + " " + p["name"] for p in parameters])
    except Exception as e:
        print "Invalid type detected, valid types are:" + str(type_mapping)
        raise e


    h_definition += param_list
    cpp_definition += param_list

    h_definition += ")"
    cpp_definition += ")"

    out["hpp"] = h_definition +";\r\n"

    cpp_definition += " {\r\n"

    cpp_definition += generate_function_body(parameters, "/" + service_key_name + microbit_query, ep_name, return_type, returns, request_type)

    cpp_definition += "}\r\n"

    out["cpp"] = cpp_definition

    return out

def parse_service(service, service_key_name, service_name, request_type):

    out = {"hpp":[],"cpp":[], "structs":[]}

    api_prefix = safe_extract("apiPrefix", service, "")
    compulsory = safe_extract("compulsoryParameters", service, [])

    query_string =  safe_extract("microbitQueryString", service, "")

    for e in service["endpoint"].keys():
        endpoint = service["endpoint"][e]

        returns = safe_extract("returns", endpoint, [])

        return_type = generate_return_type(returns, service_name, e)

        if len(return_type["struct"]) > 0:
            out["structs"] += [return_type["struct"]]

        parameters =  compulsory[:]
        parameters += safe_extract("parameters",endpoint,[])

        multi_type = False

        parameter_combinations = []

        base_params = []

        for p in parameters:
            if isinstance(p['type'], (list,)):
                multi_type = True
                continue

            base_params += [p]

        if multi_type:
            for p in parameters:
                if isinstance(p['type'], (list,)):
                    for typ in p['type']:
                        add_params = base_params[:]
                        add_params += [{
                            "name":p["name"],
                            "type":typ
                        }]
                        parameter_combinations += [add_params]

            for c in parameter_combinations:
                function_def = generate_function_definition(return_type, service_key_name, service_name, e, c, query_string, returns, request_type, api_prefix)

                out["hpp"] += [function_def["hpp"]]
                out["cpp"] += [function_def["cpp"]]

        else:
            function_def = generate_function_definition(return_type, service_key_name, service_name, e, parameters, query_string, returns, request_type, api_prefix)

            out["hpp"] += [function_def["hpp"]]
            out["cpp"] += [function_def["cpp"]]

    return out

template_location = "./templates"
out_location = "../"


template_header = open(template_location + "/template.h", "r").readlines()
template_body = open(template_location + "/template.cpp", "r").readlines()

translations = open("./translations.json")
translations = json.load(translations)

try:
    os.mkdir("../source")
except:
    print "exists"

try:
    os.mkdir("../inc")
except:
    print "exists"

for service in translations.keys():

    serviceCPPName = service + " Service"
    serviceCPPName = ''.join([s for s in serviceCPPName.title() if not s.isspace()])

    UPPER = serviceCPPName.upper()
    PASCAL = serviceCPPName

    mapping = {
        "SERVICE_NAME_UPPER" : UPPER,
        "SERVICE_NAME_PASCAL" : PASCAL,
        "SERVICE_NAMESPACE_START":"namespace " + service +" {\r\n",
        "SERVICE_NAMESPACE_USING":"using namespace " + service +";\r\n",
        "SERVICE_NAMESPACE_END":"\r\n}\r\n",
        "SERVICE_STRUCTS" : "",
        "SERVICE_MEMBER_FUNCTION_DEFINITIONS" : "",
        "SERVICE_MEMBER_FUNCTION_IMPLEMENTATIONS" : ""
    }

    for serviceEp in translations[service]:

        if safe_extract("hub_only", translations[service][serviceEp], False):
            continue

        parsed_service = parse_service(translations[service][serviceEp], service, serviceCPPName, serviceEp)

        mapping["SERVICE_STRUCTS"] += '\r\n'.join(parsed_service["structs"])
        mapping["SERVICE_MEMBER_FUNCTION_DEFINITIONS"] += tab.join(parsed_service["hpp"]) + "\r\n" + tab
        mapping["SERVICE_MEMBER_FUNCTION_IMPLEMENTATIONS"] += ''.join(parsed_service["cpp"])

        out_h_file = open(out_location + "/inc/" + serviceCPPName + ".h", "w")
        out_cpp_file = open(out_location + "/source/" + serviceCPPName + ".cpp", "w")

        out_cpp_lines = []
        out_h_lines = []

        for l in template_header:
            matches = re.findall("(%([a-zA-z]*)%)", l)

            for m in matches:
                match = m[1]

                if match in mapping.keys():
                    l = l.replace(m[0], mapping[match])
                else:
                    l = l.replace(m[0],"")

            out_h_lines += [l]

        for l in template_body:
            matches = re.findall("(%([a-zA-z]*)%)", l)

            for m in matches:
                match = m[1]

                if match in mapping.keys():
                    l = l.replace(m[0], mapping[match])
                else:
                    l = l.replace(m[0],"")

            out_cpp_lines += [l]

        out_h_file.writelines(out_h_lines)
        out_cpp_file.writelines(out_cpp_lines)


