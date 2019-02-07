#!/usr/bin/env python3
# coding: utf-8
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
    # urllib.parse is OKAY for parsing URLs -- requirements.txt
    def get_host_port(self,url):
        urlinfo = urllib.parse.urlparse(url)
        host = urlinfo.hostname
        port = urlinfo.port
        path = urlinfo.path if urlinfo.path else "/"
        if not port:
            port = 443 if url.startswith("https") else 80
        return (host, port, path)

    def connect(self, host, port):
        # From CMPUT404 Lab 02
        (family, socket_type, proto, cannon_name, sock_addr) = socket.getaddrinfo(host, port, proto=socket.SOL_TCP)[0]
        self.socket = socket.socket(family, socket_type, proto)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
    
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = b""
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer += part
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = self.get_host_port(url)
        self.connect(host, port)
        data = "GET {PATH} HTTP/1.1\r\n".format(PATH=path)
        data += "Host: {HOST}\r\n".format(HOST=host)
        data += "\r\n"
        self.sendall(data)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall(self.socket)
        print(data) # for printing user-story
        data = data.split("\r")
        index = 0
        for line in data[1:]:
            index += 1
            if ":" not in line: break
        status = int(data[0].split()[1])
        self.close()
        return HTTPResponse(status, "\r".join(data[index:]).strip())

    def POST(self, url, args=None):
        host, port, path = self.get_host_port(url)
        self.connect(host, port)
        body = ""
        if args:
            for arg in args:
                body += arg + "=" + args[arg] + "&"
            body = body[:-1] # remove the last &
        data = "POST {PATH} HTTP/1.1\r\n".format(PATH=path)
        data += "Host: {HOST}\r\n".format(HOST=host)
        data += "Content-Type: application/x-www-form-urlencoded\r\n"
        data += "Content-Length: " + str(len(body)) + "\r\n"
        data += "\r\n"
        data += body
        self.sendall(data)
        self.socket.shutdown(socket.SHUT_WR)
        data = self.recvall(self.socket)
        print(data) # for printing user-story
        data = data.split("\r")
        index = 0
        for line in data[1:]:
            index += 1
            if ":" not in line: break
        status = int(data[0].split()[1])
        self.close()
        return HTTPResponse(int(status), "\r".join(data[index:]).strip())

    def command(self, url, command="GET", args=None):
        urlinfo = urllib.parse.urlparse(url)
        if not urlinfo.hostname:
            print("Error: No hostname detected. Did you forget to add 'http://'?\n")
            exit()

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
