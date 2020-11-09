import json
import logging

from flask import Flask, g, render_template, url_for
from flask_oidc import OpenIDConnect


logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
})

 
oidc = OpenIDConnect(app)


@app.route('/')
def index():
    if oidc.user_loggedin:
        context = {"email": oidc.user_getfield('email')}
        return render_template("main.html", **context)
    else:
        return render_template("index.html")

@app.route('/private')
@oidc.require_login
def private(): 
    info = oidc.user_getinfo(['email', 'openid_id'])
    return render_template("private.html", info=info)

@app.route('/okta_pvt')
@oidc.require_login
def private_okta():
    return json.dumps({"Success": False})


@app.route('/api')
@oidc.accept_token(True, ['openid'])
def hello_api():
    return json.dumps({'hello': 'Welcome %s' % g.oidc_token_info['sub']})


@app.route('/logout')
def logout():
    oidc.logout()
    return render_template("logout.html")


if __name__ == '__main__':
    # app.run(ssl_context=('cert.pem', 'key.pem'))
    # app.run(host='sanudev', debug=True)
    # app.run(debug=True)
    app.run(debug=True, ssl_context='adhoc')
    # app.run(ssl_context=('cert.pem', 'key.pem'))



