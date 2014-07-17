from flask import Flask


app = None


def create_app():
    """
    create the main application
    """
    global app
    app = Flask(__name__)
    app.secret_key = 'lhq5./s/.erq358h9h!@OhzH^)NFsdk;jf'
    return app
