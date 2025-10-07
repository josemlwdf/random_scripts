#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

class ExtendedHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        # Print all request headers
        print("=== Received POST Headers ===")
        for key, value in self.headers.items():
            print(f"{key}: {value}")
        print("=============================")

        # Read the body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        # Save the body to a file
        with open("uploaded_file", "wb") as f:
            f.write(post_data)

        # Respond to the client
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK.\n")

    def do_GET(self):
        # Print all request headers
        print("=== Received GET Headers ===")
        for key, value in self.headers.items():
            print(f"{key}: {value}")
        print("============================")

        # Call the parent handler to serve files normally
        super().do_GET()

def run(server_class=HTTPServer, handler_class=ExtendedHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving HTTP on port {port} (GET to list/download, POST to upload)...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
