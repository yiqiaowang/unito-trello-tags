"""
HTTP request handler to get the OAUTH redirect from Trello.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler


class RequestHandler(BaseHTTPRequestHandler):
    fragment = None

    def do_GET(self):
        """ Handle GET requests. Remembers the URL for verification. """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(
            b"Authorization almost complete! You may close this window and head back to the command line.")

        RequestHandler.fragment = self.path

    def log_message(self, format, *args):
        """ Redefined to silence logging. """
        return
