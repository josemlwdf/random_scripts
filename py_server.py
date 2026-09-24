#!/usr/bin/env python3
import os
import ssl
import subprocess
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


def generate_self_signed_cert(certfile="cert.pem", keyfile="key.pem"):
    """Generates a self-signed TLS certificate and private key via OpenSSL CLI."""
    print(f"Generating self-signed certificate '{certfile}' and key '{keyfile}'...")
    cmd = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-keyout",
        keyfile,
        "-out",
        certfile,
        "-days",
        "365",
        "-nodes",
        "-subj",
        "/CN=localhost",
    ]
    try:
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("Certificate and key generated successfully.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as err:
        print(
            f"Warning: Failed to generate certificate via OpenSSL ({err}).",
            file=sys.stderr,
        )
        return False


def run(
    port=8443,
    certfile="cert.pem",
    keyfile="key.pem",
    server_class=HTTPServer,
    handler_class=ExtendedHTTPRequestHandler,
):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)

    generated_files = []

    # Automatically generate cert and key if missing, tracking what was created
    if not (os.path.exists(certfile) and os.path.exists(keyfile)):
        if not os.path.exists(certfile):
            generated_files.append(certfile)
        if not os.path.exists(keyfile):
            generated_files.append(keyfile)

        if not generate_self_signed_cert(certfile, keyfile):
            generated_files.clear()

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

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Stopping server...")
    finally:
        httpd.server_close()
        # Clean up auto-generated files on exit
        if generated_files:
            print("Cleaning up auto-generated certificate files...")
            for filepath in generated_files:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        print(f"Removed: {filepath}")
                    except OSError as err:
                        print(
                            f"Failed to remove '{filepath}': {err}",
                            file=sys.stderr,
                        )


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
