import re, requests, urllib, json, pickle, os, datetime

from radio_packet import RadioPacket
from utils import hub_regexp, safe_extract
from pathlib import Path
from datetime import timedelta
"""
A class that handles two types of micro:bit request:

(1) A REST request, which always starts with a query string, parameters following in the main body of the packet. These requests conventionally talk to a REST endpoint
(2) A Cloud Variable request, which shares a variable to a rest endpoint. Cloud variables have a namespace hash, a variable name hash, and a string value.
"""

# CONSTANSTS DEFINATIONS
PKG_WEATHER = "weather"
PKG_IOT = "iot"
PKG_ENERGY = "energy"
PKG_CARBON = "carbon"
PKG_INIT = "init"
PKG_SHARE = "share"
PKG_ISS = "iss"

PERSIST_FILE = "DataStore.txt"

PI_ID = {'piId': None, 'schoolId': None}

PI_HEADER = {'school-id': None, 'pi-id': None}


class RequestHandler:

    def __init__(self, rPacket, translations, hub_variables, cloud_ep):
        self.rPacket = rPacket
        self.hubVariables = hub_variables
        self.translations = translations
        self.cloud_ep = cloud_ep
        self.returnPacket = RadioPacket(rPacket)

        #for now, hack hub_variables into the code the uses PI_HEADER
        PI_HEADER['school-id'] = self.hubVariables['query_string']['school-id']
        PI_HEADER['pi-id'] = self.hubVariables['query_string']['pi-id']

    """
    Recursively traverse a python json structure given a dot separated path. Array indices also work here.

    query.results.channel.item.condition

    or

    query.results.channel.item.forecast[0]
    """

    def __json_recursive_find__(self, parts, json):
        if parts == []:
            return json

        if len(parts) == 1:
            head, rest = parts[0], []
        else:
            head, rest = parts[0], parts[1:]

        if isinstance(head, basestring):
            arrayMatch = head.find("[")

            if arrayMatch > -1:
                rest += [int(head[arrayMatch+1:head.find("]")])]
                head = head[:arrayMatch]

                # print rest, head

            if head not in json.keys():
                return {}

        return self.__json_recursive_find__(rest, json[head])

    """
    util to join two dicts
    """

    def __join_dicts(self, dict1, dict2):
        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3

    def replace_template_with_values(self, regular_expressions, object, values):
        # foreach regexp result from our regexps, map values from the packet into the query object
        for regExp in regular_expressions:
            for tup in regular_expressions[regExp]:
                match, key, default = tup

                value = None

                if key in values.keys():
                    value = values[key]
                elif default == "":
                    # optional
                    del object[regExp]
                    continue
                elif default:
                    value = default
                else:
                    # error
                    return self.rPacket.marshall(False)

                # coerce all into strings for now?
                if regExp in object.keys():
                    object[regExp] = object[regExp].replace(match, str(value))

        # print str(object)

    """
    given a start index, extract further objects from a radio packet, mapping them into the params object

    Returns an object with params as keys, and values from the packet as values
    """

    def extractFurtherObjects(self, index, parameters):

        ret = {}
        obj = self.rPacket.get(index)
        count = 0
        while obj is not None:
            ret[parameters[count]["name"]] = obj
            index += 1
            count += 1
            obj = self.rPacket.get(index)

        return ret

    """
    mapQueryString

    maps a microbit url string into the url format expected by the rest endpoint, extracting each into a corresponding variable:

    translations.json:
    /weather/%location%/temperature

    microbit querystring:
    /weather/lancaster,uk/temperature

    output:
    {
        "location":"lancaster,uk"
    }

    """

    def mapQueryString(self, url, urlFormat):
        part, rest = url[0], url[1:]
        out = {}

        # map parts of the packet into the querystring first.
        for format in urlFormat:
            name = re.search("%(.*)%", format)
            key = name.group(1)

            if key[-1] == "?":
                if part == None:
                    break

                key = key[:-1]

            out[key] = part

            # the line after won't work if rest is empty...
            if len(rest) == 0:
                part = None
                continue

            part, rest = rest[0], rest[1:]

        return out

    def processRESTRequest(self, url, request_type, translation, part):
        operation = translation[request_type]
        if "baseURL" in operation:
            baseURL = operation["baseURL"]

        urlFormat = [x for x in operation["microbitQueryString"].split("/") if x]

        #print "baseURL"
        #print baseURL

        # the following giant mess needs to be refactored at some point... but not now.
        if part == PKG_CARBON:
            res = 'OK'
            #print "Handle carbon package here"
            #print "method url"
            #print url
            if url[0] == "index":
                URLreq = baseURL + "intensity"
                try:
                    r = requests.get(URLreq)
                except requests.exceptions.RequestException as e:
                    print "Connection error: {}".format(e)
                    self.returnPacket.append("API CONNECTION ERROR")
                    return self.returnPacket.marshall(True)
                response = json.loads(r.text)
                #print response['data'][0]['intensity'][url[0]]
                res = response['data'][0]['intensity'][url[0]]

            if url[0] == "value":
                URLreq = baseURL + "intensity"
                try:
                    r = requests.get(URLreq)
                except requests.exceptions.RequestException as e:
                    print "Connection error: {}".format(e)
                    self.returnPacket.append("API CONNECTION ERROR")
                    return self.returnPacket.marshall(True)
                response = json.loads(r.text)
                if response['data'][0]['intensity']['actual'] is not None:
                    res = str(response['data'][0]['intensity']['actual'])
                else:
                    res = str(response['data'][0]['intensity']['forecast'])

            if url[0] == 'genmix':
                URLreq = baseURL + "generation"
                try:
                    r = requests.get(URLreq)
                except requests.exceptions.RequestException as e:
                    print "Connection error: {}".format(e)
                    self.returnPacket.append("API CONNECTION ERROR")
                    return self.returnPacket.marshall(True)
                response = json.loads(r.text)
                genmix = response['data']['generationmix']
                for gendata in genmix:
                    if gendata['fuel'] == url[1]:
                        res = str(gendata['perc'])
                        break

            #print res
            self.returnPacket.append(res)
            return self.returnPacket.marshall(True)

        if part == PKG_ENERGY:
            res = "OK"
            #print "Handle energy package here"
            #print baseURL
            #print url
            if url[0] == "energyLevel":
                if url[1] == "0":
                    URLreq = baseURL + "energy_type=ELECTRICITY"
                elif url[1] == "1":
                    URLreq = baseURL + "energy_type=GAS"
                elif url[1] == "2":
                    URLreq = baseURL + "energy_type=SOLAR"

            if url[2] == "local":
                URLreq = URLreq + "&location_uid="+PI_HEADER['school-id']
            else:
                URLreq = URLreq + "&location_uid="+url[2]

            if len(url) > 3:
                if url[3] == "historical":
                    today = datetime.datetime.today()
                    if url[4] == "hour":
                        n_hours = int(url[5])
                        FromDay = datetime.datetime.today() - timedelta(hours=n_hours)
                    if url[4] == "day":
                        n_days = int(url[5])
                        FromDay = datetime.datetime.today() - timedelta(days=n_days)
                    if url[4] == "week":
                        n_weeks = int(url[5])
                        FromDay = datetime.datetime.today() - timedelta(weeks=n_weeks)
                    if url[4] == "month":
                        n_months = int(url[5])
                        n_days = 30 * n_months
                        FromDay = datetime.datetime.today() - timedelta(days=n_days)
                    URLreq = URLreq + "&from=" + FromDay.strftime('%Y-%m-%d %H:%M:%S.%f') + "&to=" + today.strftime('%Y-%m-%d %H:%M:%S.%f')

            print URLreq

            try:
                resp = requests.get(URLreq, headers=PI_HEADER)
                print resp.status_code
		if resp.status_code == 200:
                    resJson = json.loads(resp.text)
                    if 'value' in resJson:
                        res = str(resJson['value'])
                    else:
                        res = resJson
                else:
		    res = 0

            except requests.exceptions.RequestException as e:
                print "Connection error: {}".format(e)
                self.returnPacket.append("API CONNECTION ERROR")
                return self.returnPacket.marshall(True)

            self.returnPacket.append(res)
            return self.returnPacket.marshall(True)

        if part == PKG_ISS:
            res = "OK"
            #print url[0]
            try:
                resp = requests.get(baseURL)
                resJson = json.loads(resp.text)
                #print resJson
                if url[0] == "location":
                    res = "Lat:" + \
                        str(round(resJson['latitude'], 4)) + \
                        ", Lon:" + str(round(resJson['longitude'], 4))
                elif url[0] == "solarlocation":
                    res = "Lat:" + \
                        str(round(resJson['solar_lat'], 4)) + \
                        ", Lon:" + str(round(resJson['solar_lon'], 4))
                elif url[0] == "velocity":
                    res = int(round(resJson[url[0]], 2))
                elif url[0] == "altitude":
                    res = int(round(resJson[url[0]], 2))
                elif url[0] == "daynum":
                    epoch = datetime.datetime.utcfromtimestamp(0)
                    today = datetime.datetime.today()
                    d = today - epoch
                    res = d.days
                    #res = int(round(resJson[url[0]],2))
                elif url[0] in resJson:
                    res = resJson[url[0]]

            except requests.exceptions.RequestException as e:
                print "Connection error: {}".format(e)
                self.returnPacket.append("API CONNECTION ERROR")
                return self.returnPacket.marshall(True)

            self.returnPacket.append(res)
            return self.returnPacket.marshall(True)

        if part == PKG_INIT:
            res = "OK"
            #print "Handle Init package here"
            #print "method url"
            #print url
            #print PI_ID
            id = self.rPacket.get(1)
            if id == "reset":
                if os.path.isfile(PERSIST_FILE):
                    os.remove(PERSIST_FILE)
                    #print "done"
                # else:
                    #print "not done"

            elif url[0] == "piId" or url[0] == "schoolId":
                if self.PI_ID[url[0]] is None:
                    self.PI_ID[url[0]] = id
                    file = open(PERSIST_FILE, 'w')
                    pickle.dump(self.PI_ID, file)
                    file.close()
                    print "OK"
                else:
                    res = self.PI_ID[url[0]]
                    print "Not OK"
            #print PI_ID[url[0]]
            self.returnPacket.append(res)
            return self.returnPacket.marshall(True)

        if part == PKG_SHARE:
            res = "OK"
            if PI_HEADER['school-id'] == None or PI_HEADER['pi-id'] == None:
                print "Check headers"
                print PI_HEADER
            #print "Handle share package here"
            #print "method url"
            #print url

            if url[0] == "fetchData":
                URLreq = baseURL + url[1]
                try:

                    resp = requests.get(URLreq, headers=PI_HEADER)

                except requests.exceptions.RequestException as e:
                    print "Connection error: {}".format(e)
                    self.returnPacket.append("API CONNECTION ERROR")
                    return self.returnPacket.marshall(True)
                #print URLreq
                resJson = json.loads(resp.text)
                print resJson
                if 'value' in resJson:
                    res = resJson['value']
                else:
                    res = "NOT FOUND"

            if url[0] == "shareData":
                jsonData = {'shared_with': 'SCHOOL', 'value': '0'}
                jsonData['value'] = self.rPacket.get(1)
                #jsonData['value'] = jsonData['description']
                name = self.rPacket.get(2)
                URLreq = baseURL + name + "/"
                varType = self.rPacket.get(2)
                if varType == 0:
                    jsonData['shared_with'] = 'ALL'
                else:
                    jsonData['shared_with'] = 'SCHOOL'
                print jsonData
                try:
                    resp = requests.post(
                        URLreq, headers=PI_HEADER, data=jsonData)
                except requests.exceptions.RequestException as e:
                    print "Connection error: {}".format(e)
                    self.returnPacket.append("API CONNECTION ERROR")
                    return self.returnPacket.marshall(True)
            if url[0] == "historicalData":
                jsonData = {'namespace': 'histery', 'name': ' ', 'type': 0 ,'unit':' ' , 'time':' ','value':' '}
                jsonData['value'] = self.rPacket.get(1)
                jsonData['name'] = self.rPacket.get(2)
		jsonData['namespace'] = self.rPacket.get(3)
		jsonData['unit'] = self.rPacket.get(4)
		jsonData['time'] = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
		URLreq = operation["extraURL"]
                #print jsonData
                try:
                    resp = requests.post(
                        URLreq, headers=PI_HEADER, data=jsonData)
		    #print resp
                except requests.exceptions.RequestException as e:
                    print "Connection error: {}".format(e)
                    self.returnPacket.append("API CONNECTION ERROR")
                    return self.returnPacket.marshall(True)

            #print resp
            self.returnPacket.append(res)
            return self.returnPacket.marshall(True)

         # map micro:bit query string to variables
        out = self.mapQueryString(url, urlFormat)

        #print "out maping"
        #print str(out)

        #print urlFormat

        # auth_token ='ddca3062-11ff-4116-87dc-36da9f01afe6'
        # hed = {'Authorization': 'Bearer ' + auth_token}
        # dataOn = {"commands":[{"component":"main","capability": "switch", "command":"on"}]}
        # dataOff = {"commands":[{"component":"main","capability": "switch", "command":"off"}]}

        # if part == PKG_IOT :

        # baseURL = "https://api.smartthings.com/v1/devices/1439773a-c144-41cd-9c5d-d1b03d3fe0a1/commands"

        # data1 = self.rPacket.get(1)
        # data2 = self.rPacket.get(2)

        # try:
        #     if data2 == 1:
        #         requests.post(baseURL, json=dataOn,headers=hed)
        #     else:
        #         requests.post(baseURL, json=dataOff,headers=hed)

        # except requests.exceptions.RequestException as e:
        #     print "Connection error: {}".format(e)
        #     self.returnPacket.append("API CONNECTION ERROR")
        #     return self.returnPacket.marshall(True)

        # self.returnPacket.append("OK")
        # return self.returnPacket.marshall(True)

        if part == PKG_IOT:
            res = "OK"
            if PI_HEADER['school-id'] == None or PI_HEADER['pi-id'] == None:
                print "Check headers"
                print PI_HEADER

            if request_type == "GET":
                URLreq = baseURL + url[1]

                if url[0] == "bulbState" or url[0] == "switchState":
                    URLreq = URLreq + "/switch/"

                elif url[0] == "bulbLevel":
                    URLreq = URLreq + "/switch-level/"

                elif url[0] == "bulbTemp":
                    URLreq = URLreq + "/color-temperature/"

                elif url[0] == "sensorState":
                    URLreq = URLreq + "/motion/"

                elif url[0] == "sensorTemp":
                    URLreq = URLreq + "/temperature/"

                elif url[0] == "bulbColour":
                    URLreq = URLreq + "/color-control/"

                else:
                    print "Unknown request!!!"
                    self.returnPacket.append("Unknown request!!!")
                    return self.returnPacket.marshall(True)


                try:
                    #print "URLreq:", URLreq

                    resp = requests.get(URLreq, headers=PI_HEADER)

                except requests.exceptions.RequestException as e:
                    print "Connection error: {}".format(e)
                    self.returnPacket.append("API CONNECTION ERROR")
                    return self.returnPacket.marshall(True)
                #print URLreq
                # response = {"device": "bulb", "status": {"level": "90","color": "unknown"}}
                response = json.loads(resp.text)
                #print response
                res = str(response['value'])
                # print res

            elif request_type == "POST":
                jsonData = {'value': 'off'}

                name = self.rPacket.get(1)
                URLreq = baseURL + name

                if url[0] == "bulbState" or url[0] == "switchState":
                    URLreq = URLreq + "/switch/"
                    switchState = self.rPacket.get(2)
                    if switchState == 0:
                        jsonData['value'] = 'off'
                    else:
                        jsonData['value'] = 'on'

                elif url[0] == "bulbLevel":
                    URLreq = URLreq + "/switch-level/"
                    level = self.rPacket.get(2)
                    jsonData['value'] = level

                elif url[0] == "bulbTemp":
                    URLreq = URLreq + "/color-temperature/"
                    level = self.rPacket.get(2)
                    jsonData['value'] = level

                elif url[0] == "bulbColour":
                    URLreq = URLreq + "/color-control/"
                    level = self.rPacket.get(2)
                    jsonData['value'] = level

                else:
                    print "Unknown request!!!"
                    self.returnPacket.append("Unknown request!!!")
                    return self.returnPacket.marshall(True)


                try:
                    resp = requests.post(URLreq, headers=PI_HEADER, data=jsonData)

                except requests.exceptions.RequestException as e:
                    print "Connection error: {}".format(e)
                    self.returnPacket.append("API CONNECTION ERROR")
                    return self.returnPacket.marshall(True)

            #print resp
            self.returnPacket.append(res)
            return self.returnPacket.marshall(True)

        # any code above needs to be refactored.

        # if no endpoint is specified, set a default key value of none
        if out["endpoint"] is None:
            out["endpoint"] = "none"

        # if there is no matching endpoint return error packet
        if out["endpoint"] not in operation["endpoint"].keys():
            raise self.rPacket.marshall(False)

        endpoint = operation["endpoint"][out["endpoint"]]

        # extract further objects from the packet against the keys specified in the parameters part of the translation, and join with `out`
        if "parameters" in endpoint.keys():
            out = self.__join_dicts(out, self.extractFurtherObjects(1, endpoint["parameters"]))

        regexStrings = {}

        queryObject = safe_extract("queryObject", operation, {})
        headers = safe_extract("headers", operation, {})

        # for each query field in the queryobject extract the %variable_name% pattern.
        for param in queryObject:
            regexStrings[param] = re.findall(hub_regexp, queryObject[param])

        # for each query field in the queryobject extract the %variable_name% pattern.
        for param in headers:
            regexStrings[param] = re.findall(hub_regexp, headers[param])

        # attach any hub variables that may be required in the query string
        for param in self.hubVariables["query_string"]:
            # p is the value
            p = self.hubVariables["query_string"][param]
            # provide the regexp for each enter in the regex strings, and key, with no default
            for reg in regexStrings:
                regexStrings[reg] += [("%" + param + "%", param, '')]
            # set the corresponding value in the out obj
            out[param] = p

        # to simplify code, lets lump the base url (that may require regex'ing) into the queryobj
        regexStrings["baseURL"] = re.findall(hub_regexp, baseURL)
        queryObject["baseURL"] = baseURL

        self.replace_template_with_values(regexStrings, queryObject, out)
        self.replace_template_with_values(regexStrings, headers, out)

        # remove our now regexp'd baseURL from the query object
        baseURL = queryObject["baseURL"]
        del queryObject["baseURL"]

        try:
            if request_type == "GET":
                r = requests.get(baseURL, headers=headers, params=queryObject)
            elif request_type == "POST":
                r = requests.post(baseURL, headers=headers, data=queryObject)

            print "Request sent to: %s with headers: %s and data: %s" % (baseURL, str(headers), str(queryObject))
            print str(r)
            #TODO: handle bad status codes...
        except requests.exceptions.RequestException as e:
            print "Connection error: {}".format(e)
            return self.returnPacket.marshall(False)

        if "jsonPath" in endpoint.keys():
            path = [x for x in endpoint["jsonPath"].split(".") if x]

            print path

            response = json.loads(r.text)

            jsonObj = self.__json_recursive_find__(path, response)

            returnVariables = endpoint["returns"]

            for ret in returnVariables:
                print jsonObj
                if ret["name"] in jsonObj:
                    print jsonObj[ret["name"]]
                    self.returnPacket.append(str(jsonObj[ret["name"]]))

        return self.returnPacket.marshall(True)

    def handleRESTRequest(self):
        # every rest request should have the URL as the first item.
        url = self.rPacket.get(0)

        pieces = [x for x in url.split("/") if x is not '']

        part, rest = pieces[0], pieces[1:]

        request_type = None

        if part not in self.translations.keys():
            return self.rPacket.marshall(False)

        translation = self.translations[part]

        if self.rPacket.request_type == RadioPacket.REQUEST_TYPE_GET_REQUEST:
            request_type = "GET"

        if self.rPacket.request_type == RadioPacket.REQUEST_TYPE_POST_REQUEST:
            request_type = "POST"

        return self.processRESTRequest(rest, request_type, translation, part)

    '''
    A hello packet has a status and optionally the hub or school id (at the moment..)
    0 is the status
    1 is the school id,
    2 is the hub id
    '''
    def handleHelloPacket(self):

        print "HELLO PACKET!"
        status = self.rPacket.get(0)

        print "REMEMBER TO RESTORE SCHOOL ID..."
        self.hubVariables["query_string"] = {
            "school-id":"655BD", #self.rPacket.get(1)
            "pi-id": self.rPacket.get(2)
        }

        self.hubVariables["authenticated"] = True

        self.returnPacket.append(0) # 0  means ok
        return self.returnPacket.marshall(True)

    def handleCloudVariable(self):
        namespaceHash = self.rPacket.get(0)
        variableNameHash = self.rPacket.get(1)
        value = self.rPacket.get(2)
        appId = self.rPacket.app_id

        self.cloud_ep.emit({
            "appId": appId,
            "uid": self.rPacket.uid,
            "namespace": namespaceHash,
            "variable_name": variableNameHash,
            "value": value
        })

        return self.returnPacket.marshall(True)

    def handleRequest(self):

        if self.rPacket.request_type & RadioPacket.REQUEST_TYPE_HELLO:
            return self.handleHelloPacket()

        # check packet type in order to handle request correctly
        if self.rPacket.request_type & (RadioPacket.REQUEST_TYPE_GET_REQUEST | RadioPacket.REQUEST_TYPE_POST_REQUEST):
            return self.handleRESTRequest()

        if self.rPacket.request_type & (RadioPacket.REQUEST_TYPE_CLOUD_VARIABLE):
            return self.handleCloudVariable()

        print "unrecognised packet type"
        exit(1)
