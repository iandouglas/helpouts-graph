# coding=utf-8
"""
views for general pages like the storyline, lexicon, privacy, etc
"""
from flask import render_template, get_flashed_messages


def privacy():
    """
    show our privacy data

    /privacy
    """
    return render_template('general/privacy.html',
                           flash=get_flashed_messages())


def terms_of_service():
    """
    show our terms of service

    /tos
    """
    return render_template('general/terms_of_service.html',
                           flash=get_flashed_messages())
