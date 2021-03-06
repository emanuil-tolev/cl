# -*- coding: utf-8 -*-

from flask import Flask, request, abort, render_template
from flask.views import View
from flask.ext.login import login_user, current_user

import portality.models as models
from portality.core import app, login_manager

from portality.view.account import blueprint as account
from portality.view.nav import blueprint as nav
from portality.view.media import blueprint as media
from portality.view.admin import blueprint as admin
from portality.view.graph import blueprint as graph
from portality.view.contact import blueprint as contact
from portality.view.query import blueprint as query
from portality.view.stream import blueprint as stream
from portality.view.pagemanager import blueprint as pagemanager
from portality.view.feed import blueprint as feed

from portality.view.crawler import blueprint as crawler
from portality.view.parser import blueprint as parser


app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(nav, url_prefix='/nav')
app.register_blueprint(media, url_prefix='/media')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(graph, url_prefix='/graph')
app.register_blueprint(contact, url_prefix='/contact')
app.register_blueprint(query, url_prefix='/query')
app.register_blueprint(stream, url_prefix='/stream')
app.register_blueprint(feed)
app.register_blueprint(pagemanager)

app.register_blueprint(crawler, url_prefix='/crawler')
app.register_blueprint(parser, url_prefix='/parser')


@login_manager.user_loader
def load_account_for_login_manager(userid):
    out = models.Account.pull(userid)
    return out

@app.context_processor
def set_current_user():
    """ Set some template context globals. """
    return dict(current_user=current_user, app=app)

@app.before_request
def standard_authentication():
    """Check remote_user on a per-request basis."""
    remote_user = request.headers.get('REMOTE_USER', '')
    if remote_user:
        user = models.Account.pull(remote_user)
        if user:
            login_user(user, remember=False)
    # add a check for provision of api key
    elif 'api_key' in request.values:
        res = models.Account.query(q='api_key:"' + request.values['api_key'] + '"')['hits']['hits']
        if len(res) == 1:
            user = models.Account.pull(res[0]['_source']['id'])
            if user:
                login_user(user, remember=False)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=app.config['PORT'])

