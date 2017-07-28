#!/usr/bin/env python

import os
import cgi

if 'QUERY_STRING' in os.environ:
    query = cgi.parse_qs(os.environ['QUERY_STRING'])
else:
    query = {}

a = int(query['a'][0])
b = int(query['b'][0])
c = a + b

print("Content-Type:text/javascript")
print("")
print("callback({'answer':'%s'});"%(str(c)))