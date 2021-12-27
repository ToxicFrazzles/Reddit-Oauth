import http.server
from time import sleep


class AuthServer(http.server.HTTPServer):
    token = None
    state = None

    def auth(self, state):
        self.state = state
        while self.token is None:
            sleep(0.5)
            self.handle_request()
        return self.token


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        url_param_str = self.requestline.split()[1].split("?")[-1]
        url_params = {p.split("=")[0]: p.split("=")[1] for p in url_param_str.split("&")}
        print(url_params)
        if url_params["state"] == self.server.state:
            self.server.token = url_params["code"]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorised. You can now close this browser window.")


if __name__ == "__main__":
    with http.server.HTTPServer(("127.0.0.1", 8765), RequestHandler) as server:
        print("http://127.0.0.1:8765")
        server.handle_request()

