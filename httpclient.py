#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Sashreek Magan
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(re.search(r"HTTP/\d.\d (\d+)", data).group(1))

    def get_headers(self,data):
        headers = data.split("\r\n\r\n", 1)[0]
        return headers.split("\r\n")[1:]

    def get_body(self, data):
        body =  data.split("\r\n\r\n", 1)[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse_url(self, url):
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path or "/"
        return path, parsed_url.hostname, parsed_url.port or 80

    def GET(self, url, args=None):
        path, host, port = self.parse_url(url)
    
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Accept: */*\r\n"
            "Connection: close\r\n\r\n"
        )
        
        self.connect(host, int(port))
        self.sendall(request)
        received = self.recvall(self.socket)
        self.close()

        code = self.get_code(received)
        body = self.get_body(received)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        path, host, port = self.parse_url(url)
        
        path, host, port = self.parse_url(url)
        data = urllib.parse.urlencode(args) if args else ""

        request = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(data)}\r\n"
            "Accept: */*\r\n"
            "Connection: close\r\n\r\n"
            f"{data}"
        )
        
        self.connect(host, int(port))
        self.sendall(request)
        received = self.recvall(self.socket)
        self.close()

        code = self.get_code(received)
        body = self.get_body(received)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
