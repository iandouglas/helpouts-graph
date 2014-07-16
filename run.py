# coding=utf-8
import os
import sys

sys.path.insert(1, os.path.join(os.path.abspath('.'), 'packages'))

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='application/*')
    COV.start()

from application import create_app

app = create_app()

from application.routes import create_routes
create_routes(app)

# if app.debug:
#     app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
