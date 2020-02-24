from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import urllib

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        fi = open('/home/ncadmin/links', 'rb')
        response = BytesIO(fi.read())
        fi.close()
        self.wfile.write(response.getvalue())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        response = BytesIO()
        response.write(b'Received: ')
        response.write(body)
        response.write('\n')
        self.wfile.write(response.getvalue())
        fo = open('/home/ncadmin/links', "ab")
        fo.write(urllib.unquote(body[4:]))
        fo.write(b'\n')
        fo.close()


httpd = HTTPServer(('', 8123), SimpleHTTPRequestHandler)
httpd.serve_forever()

