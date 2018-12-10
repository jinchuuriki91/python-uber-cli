import os
import requests
import webbrowser
from urlparse import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

API_BASE_URL = "https://api.uber.com/v1.2"
LOGIN_BASE_URL = "https://login.uber.com/oauth/v2"

START_LOCATION = (12.9084755,77.6487299)
END_LOCATION = (12.9071094,77.6426714)

class ReqHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        authorize_client(query_components["code"])


def get_profile_info(access_token, token_type):
    headers = {
        "Authorization": "%s %s" % (token_type, access_token),
        "Content-Type": "application/json",
        "Accept-Language": "en_US"
    }
    resp = requests.get("%s/me" % API_BASE_URL, headers=headers)
    print resp.json()

def get_ride_estimate(access_token, token_type):
    headers = {
        "Authorization": "%s %s" % (token_type, access_token),
        "Content-Type": "application/json",
        "Accept-Language": "en_US"
    }
    body = {
        "start_latitude": START_LOCATION[0],
        "start_longitude": START_LOCATION[1],
        "end_latitude": END_LOCATION[0],
        "end_longitude": END_LOCATION[1]
    }
    resp = requests.post("%s/requests/estimate" % API_BASE_URL, json=body, headers=headers)
    print resp.json()

def authorize_client(authorize_code):
    body = {
        "client_id": os.environ.get("UBER_CLIENT_ID"),
        "client_secret": os.environ.get("UBER_CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "scope": "profile",
        "code": authorize_code,
        "redirect_uri": "http://localhost:8000/redirect"
    }
    resp = requests.post("%s/token" % LOGIN_BASE_URL, data=body)
    resp.raise_for_status()
    json_data = resp.json()
    access_token = json_data["access_token"]
    token_type = json_data["token_type"]
    get_ride_estimate(access_token, token_type)


def run(server_class=HTTPServer, request_handler=ReqHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, request_handler)
    resp = httpd.handle_request()
    return resp

def main():
    url = "%s/authorize?response_type=code&client_id=%s&redirect_uri=http://localhost:8000/redirect" % (LOGIN_BASE_URL, os.environ.get("UBER_CLIENT_ID"))
    webbrowser.open(url)
    run()

if __name__ == "__main__":
    main()