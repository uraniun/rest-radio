from utils import safe_extract, hub_regexp
import re, requests, urllib, json, time

class URLPoller:

    def __init__(self, url, poll_time):
        self.last = int(time.time())
        self.url = url
        self.poll_time = poll_time
        self.cached = None

    def poll(self):

        now = int(time.time())

        if now - self.last < self.poll_time:
            return False

        self.last = now

        res = requests.get(self.url)

        diff = []

        response_json = res.json()

        if self.cached:
            diff += [[r] for r in response_json.keys() if r not in self.cached.keys()]
        else:
            for r in response_json.keys():
                record = response_json[r]
                diff += [record]

        self.cached = response_json

        return len(diff) > 0

    def get_cached(self):
        return self.cached
