# -*- coding: utf-8 -*-
import http.server

class MyHandler(http.server.CGIHTTPRequestHandler):
    def __init__(self, req, client_addr, server):
        http.server.CGIHTTPRequestHandler.__init__(
            self, req, client_addr, server)
def main():
    server_address = ("", 8000)
    httpd = http.server.HTTPServer(server_address, MyHandler)
    print("Server:{0}".format(server_address))
    httpd.serve_forever()

if __name__ == '__main__':
    main()