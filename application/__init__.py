from flask import Flask


app = None


def create_app():
    """
    create the main application
    """
    global app
    app = Flask(__name__)
    return app
