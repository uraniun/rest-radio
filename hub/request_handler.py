from radio_packet import RadioPacket
import re, requests,urllib,json

class RequestHandler:

    def __init__(self, rPacket, translations):
        self.rPacket = rPacket
        self.translations = translations

        self.returnPacket = RadioPacket(rPacket)

    # need to include array indexing...
    def __json_recursive_find__(self, parts, json):
        if parts == []:
            return json

        if len(parts) == 1:
            head, rest = parts[0],[]
        else:
            head, rest = parts[0], parts[1:]

        if head not in json.keys():
            return {}

        return self.__json_recursive_find__(rest,json[head])

    def __join_dicts(self,dict1,dict2):
        dict3 = dict1.copy()
        dict3.update(dict2)
        return dict3

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

    def mapQueryString(self, url, urlFormat):
        part, rest = url[0],url[1:]
        out = {}

        # map parts of the packet into the querystring first.
        for format in urlFormat:
            name = re.search("%(.*)%",format)
            key = name.group(1)

            if key[-1] == "?":
                if part == None:
                    break

                key = key[:-1]

            out[key] = part

            # the line below won't work if rest is empty...
            if len(rest) == 0:
                part = None
                continue

            part, rest = rest[0], rest[1:]
        
        return out

    def processRESTRequest(self, url, request_type, translation):
        operation = translation[request_type]
        baseURL = operation["baseURL"]
        queryObject = operation["queryObject"]
        urlFormat = [x for x in operation["microbitQueryString"].split("/") if x]

        # map micro:bit query string to variables
        out = self.mapQueryString(url,urlFormat)

        print str(out)

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

        # for each query field in the queryobject extract the %variable_name% pattern.
        for param in queryObject:
            regexStrings[param] = re.findall(r"(%([a-zA-z]*)(?:\?=)?([a-z]*)%)",queryObject[param])

        # to simplify code, lets lump the base url (that may require regex'ing) into the queryobj
        regexStrings["baseURL"] = re.findall(r"(%([a-zA-z]*)(?:\?=)?([a-z]*)%)",baseURL)
        queryObject["baseURL"] = baseURL

        # foreach regexp result from our regexps, map values from the packet into the query object
        for regExp in regexStrings:
            for tup in regexStrings[regExp]:
                match, key, default = tup

                value = None

                if key in out.keys():
                    value = out[key]
                elif default == "":
                    # optional
                    del queryObject[regExp]
                    continue
                elif default:
                    value = default
                else:
                    # error
                    return self.rPacket.marshall(False)

                #coerce all into strings for now?
                queryObject[regExp] = queryObject[regExp].replace(match,str(value))

        print str(queryObject)

        # remove our now regexp'd baseURL from the query object
        baseURL = queryObject["baseURL"]
        del queryObject["baseURL"]

        if request_type == "GET":
            r = requests.get(baseURL, params= queryObject)
        elif request_type == "POST":
            r = requests.post(baseURL, data= queryObject)

        if "jsonPath" in endpoint.keys():
            path = [x for x in endpoint["jsonPath"].split(".") if x]

            response = json.loads(r.text)

            jsonObj = self.__json_recursive_find__(path, response)

            returnVariables = endpoint["returns"]

            for ret in returnVariables:
                print jsonObj[ret["name"]]
                self.returnPacket.append(jsonObj[ret["name"]])
        

        return self.returnPacket.marshall(True)

    def handleRESTRequest(self):

        # every rest request should have the URL as the first item.
        url = self.rPacket.get(0)

        pieces = [x for x in url.split("/") if x is not '']

        print pieces

        part, rest = pieces[0],pieces[1:]

        request_type = None

        translation = self.translations[part]

        if self.rPacket.request_type == RadioPacket.REQUEST_TYPE_GET_REQUEST:
            request_type = "GET"

        if self.rPacket.request_type == RadioPacket.REQUEST_TYPE_POST_REQUEST:
            request_type = "POST"

        return self.processRESTRequest(rest, request_type, translation)

    def handleRequest(self):
        # check packet type in order to handle request correctly future extensions may not be REST types.
        if self.rPacket.request_type & (RadioPacket.REQUEST_TYPE_GET_REQUEST | RadioPacket.REQUEST_TYPE_POST_REQUEST | RadioPacket.REQUEST_TYPE_DELETE_REQUEST | RadioPacket.REQUEST_TYPE_PUT_REQUEST) :
            return self.handleRESTRequest()

        