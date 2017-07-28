#!/usr/bin/env python
import os, json
import cgi, cgitb
from markov import make_reply

cgitb.enable()
form = cgi.FieldStorage()

#callbackでmake_reply作成して送る
def main():
    m = form.getvalue("m", default="")

    if m == "": show_form()
    elif m == "say": api_say()

def api_say():
    txt = form.getvalue("txt", default="")
    print("Content-Type: text/plain; charset=utf-8")
    print("")
    if txt == "": return
    res = make_reply(txt)
    print(res)

def show_form():
    print("Content-Type: text/plain; charset=utf-8")
    print("")
    txt = "show_form"
    print(txt)
    #print("callback({'txt':'hullo'});")

main()




"""
dict_file = "log.json"
dic = { 'm': m, 'txt': txt }
json.dump(dic,open(dict_file,"w",encoding="utf-8"))
"""