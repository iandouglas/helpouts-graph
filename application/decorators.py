# coding=utf-8
"""
decorators.py

Decorators for URL handlers

"""
from functools import wraps

from google.appengine.api import users
from flask import redirect, request, url_for, flash

from application.models.user import User
from application.models.user_settings import UserSettings


def login_required(func):
    """
    Requires user to be logged into Google

    ** EXCLUDED FROM TEST COVERAGE **
    TODO: un-exclude this code once we get integration tests done

    :param func:
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        """
        decorated view
        :param args:
        :param kwargs:
        """
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)  # pragma: no cover
    return decorated_view


def registration_required(func):
    """
    Requires user to be registered

    ** EXCLUDED FROM TEST COVERAGE **
    TODO: un-exclude this code once we get integration tests done

    :param func:
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        """
        decorated view
        :param args:
        :param kwargs:
        """
        guser = users.get_current_user()
        user = User.query().filter(User.guser == guser).get()
        user_settings = UserSettings.query().filter(UserSettings.guser == guser).get()

        if not user or not user_settings:
            return redirect(url_for('register'))
        return func(*args, **kwargs)  # pragma: no cover
    return decorated_view


def is_lrv(func):
    """
    Requires user to be (l)ogged in, (r)egistered, and (v)erified

    ** EXCLUDED FROM TEST COVERAGE **
    TODO: un-exclude this code once we get integration tests done

    :param func:
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        """
        decorated view
        :param args:
        :param kwargs:
        """
        guser = users.get_current_user()
        if not guser:
            return redirect(users.create_login_url(url_for('home')))

        user_settings = UserSettings.query().filter(UserSettings.guser == guser).get()
        if not user_settings:
            return redirect(url_for('register'))

        if not user_settings.verified:
            return redirect(url_for('still_need_to_verify'))

        return func(*args, **kwargs)  # pragma: no cover
    return decorated_view


def bounce_if_already_verified(func):
    """
    user is verified and will not be able to reach the verification or resend verification email pages
    :param func:
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        """
        decorated view
        :param args:
        :param kwargs:
        """
        guser = users.get_current_user()
        user_settings = UserSettings.query().filter(UserSettings.guser == guser).get()
        if user_settings and user_settings.verified:
            return redirect(url_for('cmd'), code=302)
        return func(*args, **kwargs)  # pragma: no cover
    return decorated_view


def bounce_if_already_registered(func):
    """
    user is registered and will not be able to reach the registration pages
    :param func:
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        """
        decorated view
        :param args:
        :param kwargs:
        """
        guser = users.get_current_user()
        user_settings = UserSettings.query().filter(UserSettings.guser == guser).get()
        if user_settings:
            return redirect(url_for('still_need_to_verify'))
        return func(*args, **kwargs)  # pragma: no cover
    return decorated_view


def need_tutorial_step(tutorial_step):
    """
    check a user's tutorial_step value to know whether they're allowed to be here or not
    :param tutorial_step:
    """
    def real_decorator(func):
        """
        decorator
        :param func:
        """
        def wrapper(*args, **kwargs):
            """
            decorator
            :param kwargs:
            :param args:
            """
            guser = users.get_current_user()
            user_settings = UserSettings.query().filter(UserSettings.guser == guser).get()
            if not user_settings or user_settings.tutorial_step < tutorial_step:
                flash(u'Global Command needs you to finish more training before you can do that.', 'warning')
                return redirect(url_for('tutorial'))
            return func(*args, **kwargs)  # pragma: no cover
        return wrapper
    return real_decorator
