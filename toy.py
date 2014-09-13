import tornado
import os

import json

import tornado.options
from tornado.log import app_log
from tornado.web import RequestHandler
from tornado.auth import OAuth2Mixin
from tornado import gen, web

from tornado.httputil import url_concat

import tornado.httpclient

from tornado.httpclient import HTTPRequest, AsyncHTTPClient

class RootHandler(RequestHandler):
    @web.authenticated
    def get(self):
        self.write("Welcome")

class GitHubMixin(OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"

class GitHubLoginHandler(RequestHandler, GitHubMixin):
    @gen.coroutine
    def get(self):
        yield self.authorize_redirect(
            redirect_uri='http://127.0.0.1:8777/oauth',
            client_id=self.settings['github_client_id'],
            scope=[], # 
            response_type='code')

class GitHubOAuthHandler(RequestHandler):
    @web.asynchronous
    def get(self):
        
        # TODO: Check the state argument
        
        if self.get_argument("code", False):
            
            code = self.get_argument("code")
            self.write("<pre>" + code + u"</pre>\n")
            
            # TODO: Configure the curl_httpclient for tornado
            http_client = tornado.httpclient.AsyncHTTPClient()
            
            # Exchange the OAuth code for a GitHub Access Token
            #
            # POST https://github.com/login/oauth/access_token
            
            # client_id	string	Required. The client ID you received from GitHub when you registered.
            # client_secret	string	Required. The client secret you received from GitHub when you registered.
            # code	string	Required. The code you received as a response to Step 1.
            # redirect_uri	string	The URL in your app where users will be sent after authorization.
            
            # GitHub specifies a POST request yet requires URL parameters
            params = dict(
                    client_id=self.settings['github_client_id'],
                    client_secret=self.settings['github_client_secret'],
                    code=code
            )
            
            url = url_concat("https://github.com/login/oauth/access_token",
                             params)
            
            req = HTTPRequest(url,
                              method="POST",
                              headers={"Accept": "application/json"},
                              body='' # Required body
                              )
            http_client.fetch(req, callback=self.on_access)
            
        else:
            # Using web.asynchoronous, must explicitly finish
            # This should be a 40x
            self.finish()
    
    @web.asynchronous
    def on_access(self, response):
        self.write(response.body)
        
        # Use the Access Token to get the username and email address of the user
        self.finish()

def main():
    tornado.options.parse_command_line()
    handlers = [
        (r"/", RootHandler),
        (r"/login", GitHubLoginHandler),
        (r"/oauth", GitHubOAuthHandler)
    ]

    settings = dict(
        cookie_secret="supersecret",
        login_url="/login",
        xsrf_cookies=True,
        github_client_id=os.environ["GITHUB_CLIENT_ID"],
        github_client_secret=os.environ["GITHUB_CLIENT_SECRET"],
        github_scope="",
        debug=True,
        autoescape=None
    )
    
    port = 8777
    
    app_log.info("Listening on {}".format(port))

    application = tornado.web.Application(handlers, **settings)
    application.listen(port)
    tornado.ioloop.IOLoop().instance().start()

if __name__ == "__main__":
    main()