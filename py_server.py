#!/usr/bin/env python3
import os
import ssl
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler


class ExtendedHTTPRequestHandler(SimpleHTTPRequestHandler):

    def do_POST(self):
        # Print all request headers
        print("=== Received POST Headers ===")
        for key, value in self.headers.items():
            print(f"{key}: {value}")
        print("=============================")

        # Read the body
        content_length = int(self.headers.get("Content-Length", 0))
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


def run(
    port=8443,
    certfile="cert.pem",
    keyfile="key.pem",
    server_class=HTTPServer,
    handler_class=ExtendedHTTPRequestHandler,
):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)

    # Enable HTTPS if certificate and key files exist
    if os.path.exists(certfile) and os.path.exists(keyfile):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        scheme = "HTTPS"
    else:
        scheme = "HTTP"
        print(
            f"Notice: '{certfile}' or '{keyfile}' not found. Running over unencrypted HTTP."
        )

    print(
        f"Serving {scheme} on port {port} (GET to list/download, POST to upload)..."
    )
    httpd.serve_forever()


if __name__ == "__main__":
    port = 8443
    certfile = "cert.pem"
    keyfile = "key.pem"

    # Positional arguments: script.py [port] [certfile] [keyfile]
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) > 2:
        certfile = sys.argv[2]
    if len(sys.argv) > 3:
        keyfile = sys.argv[3]

    run(port=port, certfile=certfile, keyfile=keyfile)
