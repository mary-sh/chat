import time
import json
import urllib
import hashlib
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

MESSAGE_LIMIT = 10
MESSAGE_MAX_LENGTH = 400


def index():
    with open('index.html', 'r') as f:
        template = f.read()
    return template


computed_colors = {}


def generate_color(text):
    if text not in computed_colors:
        color = ('#%s' % (hashlib.md5(text or 'FFFUUUuu').hexdigest()[-6:])).upper()
        computed_colors[text] = color
    return computed_colors[text]



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
            message = dict(
                author=author,
                text=text[:MESSAGE_MAX_LENGTH],
                time=time.time(),
                color=generate_color(author.encode('utf-8'))
            )
            self.messages.append(message)
            if len(self.messages) > MESSAGE_LIMIT:
                del self.messages[0]
        except (IndexError, KeyError):
            raise

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.write_result(message, 'application/json')


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ChatHTTPRequestHandler)
    httpd.serve_forever()
