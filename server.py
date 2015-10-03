import urllib
import json
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler


def index():
    with open('index.html', 'r') as f:
        template = f.read()
    return template


class ChatHTTPRequestHandler(BaseHTTPRequestHandler):
    messages = []

    def write_result(self, data, context_type):
        if context_type == 'application/json':
            data = json.dumps(data)
        self.wfile.write(bytes(data, 'utf-8'))

    def do_GET(self):
        if self.path == '/':
            code, content_type = 200, 'text/html'
            data = index()
        elif self.path == '/messages/':
            code, content_type = 200, 'application/json'
            data = self.messages
        else:
            code, content_type = 404, 'text/html'
            data = 'Not found'

        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.write_result(data, content_type)

    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        raw_data = self.rfile.read(length)
        post_data = urllib.parse.parse_qs(raw_data.decode('utf-8'))
        try:
            author = str(post_data['author'][0])
            text = str(post_data['text'][0])
            self.messages.append(dict(author=author, text=text))
            if len(self.messages) > 100:
                pass
        except (IndexError, KeyError):
            raise

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ChatHTTPRequestHandler)
    httpd.serve_forever()
