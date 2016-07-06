#coding=utf-8
from HTMLParser import HTMLParser
import re

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.count = {}
        self.pre_leak = None
        self.get_leak = False
        self.get_level = -1

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and attrs[1][1] == '#':
            self.get_leak = True

    def handle_endtag(self, tag):
        if self.get_leak:
            self.get_leak = False

    def handle_data(self, data):
        if self.get_level >= 0:
            self.get_level -= 1
        if self.get_level == 0:
            self.count[self.pre_leak]['level'] = data
        if self.get_leak :
            if data not in self.count:
                self.count[data] = {'ips':[],'level':-1}
            self.pre_leak = data
        reg = re.compile(r"(?<![0-9.])((2[0-4][0-9]|25[0-5]|[01]?[0-9]{1,2})\.){3}(2[0-4][0-9]|25[0-5]|[01]?[0-9]{1,2})(?![0-9.])")
        m = reg.search(data)
        if m:
            self.count[self.pre_leak]['ips'].append(m.group(0))
        elif data == "威胁分值":
            self.get_level = 3

file = open("index.html")

output = ''.join(file.readlines())
parser = MyHTMLParser()
parser.feed(output)


result = {}

for leak,ips_level in parser.count.items():
    for ip in ips_level['ips']:
        if ip not in result:
            result[ip] = []
        result[ip].append((leak,ips_level['level']))

for ip in result:
    result[ip] = sorted(result[ip],key = lambda t:t[1],reverse=True)
    print ip
    print "======================"
    for leak,level in result[ip]:
        print leak + " level: " + str(level)
    print "======================"
    print ""


