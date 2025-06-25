from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

class ExtendedHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        with open("uploaded_file", "wb") as f:
            f.write(post_data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"File uploaded successfully.\n")

def run(server_class=HTTPServer, handler_class=ExtendedHTTPRequestHandler, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving HTTP on port {port} (GET to list/download, POST to upload)...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
