import tornado
import os

import tornado.options
from tornado.log import app_log
from tornado.web import RequestHandler
from tornado.auth import OAuth2Mixin
from tornado import gen, web

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
        if self.get_argument("code", False):
            code = self.get_argument("code")
            self.write(code)            
        else:
            yield self.authorize_redirect(
                    redirect_uri='http://127.0.0.1:8777/oauth',
                    client_id=self.settings['github_client_id'],
                    scope=[],
                    response_type='code',
                    extra_params={})


def main():
    tornado.options.parse_command_line()
    handlers = [
        (r"/", RootHandler),
        (r"/oauth", GitHubLoginHandler),
    ]

    settings = dict(
        cookie_secret="supersecret",
        login_url="/oauth",
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