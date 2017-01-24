"""
Trello OAuth 1 Module

This module provides functionality to help authorize
the application with Trello.
"""
import json
import server
from requests_oauthlib import OAuth1Session
from webbrowser import open_new

TRELLO_URL = {
    'request': 'https://trello.com/1/OAuthGetRequestToken',
    'authorize': 'https://trello.com/1/OAuthAuthorizeToken',
    'access': 'https://trello.com/1/OAuthGetAccessToken'
}


def construct_params(port):
    TRELLO_AUTH_PARAMS = {
        'name': 'TTags',
        'scope': 'read,write',
        'expiration': '1day',
        'callback_method': 'fragment',
        'return_url': 'http://localhost:{}'.format(port)
    }
    return TRELLO_AUTH_PARAMS


def get_credentials(path):
    """
    Get client credentials for Trello OAuth authorization.
    """
    with open(path) as json_data:
        data = json.load(json_data)
    return data


def accept_request(handler, port):
    """Starts up a http server at localhost:[port] and listens for the OAuth redirect."""
    print('Awaiting OAuth redirect on localhost:{}'.format(port))
    http_server = server.HTTPServer(('localhost', port), handler)
    http_server.handle_request()
    return handler


def authorize(port):
    """Complete OAuth authentication flow. Reads client key and secret from config file."""
    client_info = get_credentials('./ttags/client_credentials.json')
    client_key = client_info.get('client_key')
    client_secret = client_info.get('client_secret')

    # Obtain request token, 1st step
    oauth = OAuth1Session(client_key, client_secret=client_secret)
    request_url = TRELLO_URL.get('request')
    request_response = oauth.fetch_request_token(request_url)

    resource_owner_key = request_response.get('oauth_token')
    resource_owner_secret = request_response.get('oauth_token_secret')

    # Obtain authorization token, 2nd step
    authorization_url = oauth.authorization_url(
        TRELLO_URL.get('authorize'), **construct_params(port))
    open_new(authorization_url)
    print("Check your browser! Login to Trello in the new tab to authorize this application.")

    # startup server to listen to response
    Handler = server.RequestHandler
    accept_request(Handler, port)
    oauth_response = oauth.parse_authorization_response(Handler.fragment)
    verifier = oauth_response.get('oauth_verifier')

    # Obtain access token
    access_url = TRELLO_URL.get('access')

    # Create new session with all credentials, 3rd step of OAuth
    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=resource_owner_key,
                          resource_owner_secret=resource_owner_secret,
                          verifier=verifier)

    # Get the tokens
    oauth_tokens = oauth.fetch_access_token(access_url)
    access_token = oauth_tokens.get('oauth_token')
    access_token_secret = oauth_tokens.get('oauth_token_secret')

    return {
        'key': client_key,
        'token': access_token,
        'token_secret': access_token_secret
    }
