import mimetypes
import pathlib
import os
import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from jinja2 import Environment, FileSystemLoader


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        self.save_to_file(data_dict)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == "/":
            self.send_html_file(filename="index.html")
        elif pr_url.path == "/message":
            self.send_html_file(filename="message.html")
        elif pr_url.path == "/read":
            env = Environment(loader=FileSystemLoader("."))
            self.render_read_page(env)
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file(filename="error.html", status=404)

    def render_read_page(self, env):
        file_path = "storage/data.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = {}

        template = env.get_template("read.html")
        rendered_page = template.render(messages=messages)
        self.send_html_file(content=rendered_page)

    def send_html_file(self, content=None, filename=None, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        if content:
            self.wfile.write(content.encode("utf-8"))
        elif filename:
            try:
                with open(filename, "rb") as fd:
                    self.wfile.write(fd.read())
            except FileNotFoundError:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"File not found")

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()

        try:
            with open(f".{self.path}", "rb") as file:
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Static file not found")

    def save_to_file(self, data_dict):
        file_path = "storage/data.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        new_entry = {timestamp: data_dict}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        existing_data.update(new_entry)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        print("Server is running on port 3000...")
        http.serve_forever()
    except KeyboardInterrupt:
        print("Server is shutting down...")
        http.server_close()


if __name__ == "__main__":
    run()
