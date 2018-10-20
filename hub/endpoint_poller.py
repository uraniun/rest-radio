from utils import safe_extract, hub_regexp
import re, requests, urllib, json

class EndpointPoller:

    polling_endpoints = []
    url_index = 0
    hub_variables = {}
    poll_urls = []
    cached_response = {}

    def __init__(self, translations, hub_variables):

        self.hub_variables = hub_variables

        # extract any EP's which require polling.
        for ep in translations.keys():
            if "POLL" in translations[ep].keys():
                self.polling_endpoints += [translations[ep]["POLL"]]

        self.generate_urls()

    def generate_urls(self):
        self.poll_urls = []

        for polling_eps in self.polling_endpoints:
            url = safe_extract("baseURL",polling_eps,"")

            endpoints = safe_extract("endpoint", polling_eps,[])

            if len(endpoints) == 0:
                self.poll_urls += [url]
                continue

            params = re.findall(hub_regexp, url)

            for ep_key in endpoints.keys():
                ep = endpoints[ep_key]
                trans_param = safe_extract("parameters",ep,[])

                # copy
                ep_url = url[:]

                # match regexp
                for regexp in params:
                    regex, name, default = regexp[0],regexp[1],regexp[2]

                    # special case for endpoint
                    if name == "endpoint":
                        ep_url = ep_url.replace(regex,ep_key)
                    else:
                    # otherwise, check if this parameter is required by our endpoint params object
                        match = False

                        for p in trans_param:
                            if p["name"] == name:
                                match = True

                        #if it is matched, replace
                        if match:
                            ep_url = ep_url.replace(regex, self.hub_variables[name])
                        else:
                            ep_url = ep_url.replace(regex,"")

                self.poll_urls += [ep_url]

    def poll(self):
        if len(self.poll_urls) == 0:
            return

        print self.poll_urls[self.url_index]
        res = requests.get(self.poll_urls[self.url_index])

        cached = safe_extract(self.poll_urls[self.url_index], self.cached_response, None)

        diff = []

        response_json = res.json()

        if cached:
            print "cached"
            print cached
            diff += [[r] for r in response_json.keys() if r not in cached.keys()]
            for r in response_json.keys():
                record = response_json[r]

                if r not in cached.keys():
                    diff += [record]
        else:
            for r in response_json.keys():
                record = response_json[r]
                diff += [record]

        # TODO: package and return a radio packet....

        self.cached_response[self.poll_urls[self.url_index]] = response_json
        self.url_index = (self.url_index + 1) % len(self.poll_urls)

        return diff
        # exit(0)
