# coding=utf-8
from flask import render_template
# from google.appengine.api import users, memcache, urlfetch
#from application.models.user_settings import UserSettings
from application.views import warmup, home, general, graph


def create_routes(app):
    """
    URL dispatch rules

    :param app:

    format:
    app.add_url_rule:
        param 1: URL route that Flask should answer on
        param 2: the 'endpoint' alias, used in url_for('home') types of calls
        param 3: the view function to call, typically pointing into views.py like
            views.methodname, or
            views.module.methodname
        param 4: options, like which methods (HTTP verbs) to allow on this call; default just allows GET, if you know
            you're going to POST/PUT/DELETE content to the route, you'll need to set methods=[] yourself, such as
            methods=['GET','PUT','DELETE']
    """

    def build_routes(app):  # pragma: no cover
        """
        build routes for Flask
        :param app:
        """
        # App Engine warm up handler
        # this code is what App Engine calls when starting up a new instance; we could set this up to email us whenever
        #  a new instance is started, if we cared about that sort of thing.
        # See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
        app.add_url_rule('/_ah/warmup', endpoint='warmup',
                         view_func=warmup,
                         methods=['GET'])

        # app.add_url_rule('/login', endpoint='login',
        #                  view_func=login,
        #                  methods=['GET'])

        app.add_url_rule('/graph', endpoint='tos',
                         view_func=graph,
                         methods=['GET', 'POST'])
        app.add_url_rule('/graph/<string:state>', endpoint='tos',
                         view_func=graph,
                         methods=['GET', 'POST'])

        # app.add_url_rule('/tos', endpoint='tos',
        #                  view_func=general.terms_of_service,
        #                  methods=['GET'])

        app.add_url_rule('/', endpoint='home',
                         view_func=home,
                         methods=['GET'])

    build_routes(app)  # pragma: no cover

    ## Error handlers
    # Handle 404 errors
    @app.errorhandler(404)
    def page_not_found(e):  # pragma: no cover
        """
         handle 404 errors
        """
        return render_template('404.html'), 404

    # Handle 500 errors
    @app.errorhandler(500)
    def server_error(e):  # pragma: no cover
        """
        handle 500 crashes
        """
        return render_template('500.html'), 500

    @app.before_request
    def before_request():  # pragma: no cover
        """
        do this stuff before every request gets handled anywhere else
        """
        pass
