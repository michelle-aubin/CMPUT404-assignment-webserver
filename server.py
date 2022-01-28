#  coding: utf-8
import os
import socketserver

# Copyright 2022 Michelle Aubin
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'www')


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.data = self.data.decode().split('\r\n')
        method, path, _ = self.data[0].split()

        if method != "GET":
            self.send_error(405)
            return

        if '../' in path:
            self.send_error(404)
            return

        if os.path.isfile(ROOT + path):
            self.serve_file(ROOT + path)
        elif os.path.isdir(ROOT + path):
            self.serve_dir(path)
        else:
            self.send_error(404)

    def send_data(self, msg, content):
        msg += content
        self.request.sendall(bytearray(msg, 'utf-8'))

    def send_error(self, code):
        if code == 404:
            content = "Not Found"
        elif code == 405:
            content = "Method Not Allowed"

        msg = f"HTTP/1.1 {code} {content}\r\nServer: mich-server\r\nContent-Type: text/html\r\nContent-Length: {len(content.encode())}\r\n\r\n"
        self.send_data(msg, content)

    def serve_dir(self, path):
        if path[-1] != "/":
            for d in self.data:
                if d[:6] == 'Host: ':
                    host = d[6:]
                    break
            
            content = "Moved Permanently"
            msg = f"HTTP/1.1 301 {content}\r\nLocation: http://{host}{path}/\r\nServer: mich-server\r\nContent-Type: text/html\r\nContent-Length: {len(content.encode())}\r\n\r\n"
            self.send_data(msg, content)

        index_path = os.path.join(ROOT + path, 'index.html')
        if os.path.exists(index_path):
            self.serve_file(index_path)
        else:
            self.send_error(404)

    def serve_file(self, path):
        ext = os.path.splitext(path)[1]
        with open(path, 'r') as f:
            content = f.read()

        if ext == '.html':
            msg = f"HTTP/1.1 200 OK\r\nServer: mich-server\r\nContent-Type: text/html\r\nContent-Length: {len(content.encode())}\r\n\r\n"
            self.send_data(msg, content)
        elif ext == '.css':
            msg = f"HTTP/1.1 200 OK\r\nServer: mich-server\r\nContent-Type: text/css\r\nContent-Length: {len(content.encode())}\r\n\r\n"
            self.send_data(msg, content)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
