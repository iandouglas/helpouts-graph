# coding=utf-8
"""
View handlers for login, home and warmup
"""
import StringIO
import csv
import logging
from flask import render_template, session
from flask import request
from google.appengine.api import memcache
import time


def home():  # pragma: no cover
    """
    controller for the home page
    :return: flask response
    """
    session['sid'] = int(time.time())
    return render_template('index.html')


def csvstring2dict(data):
    """
    returns a list of CSV rows from provided raw string data
    :param data: string, raw CSV data read from file
    :return: list, of CSV dictionaries
    """
    csv_reader = csv.DictReader(StringIO.StringIO(data))
    return [row for row in csv_reader]


def make_cache_key(session_id, suffix):
    """
    generate a memcache-friendly key name
    :param session_id: string
    :param suffix: string
    :return: string, concatenated as-is, but this may change, thus the abstraction
    """
    return '_'.join([str(session_id), suffix])


def csv_processor(raw_csv_data):
    """
    placeholder for where we'll be slicing and dicing the CSV data ourselves to correct known issues
    :param raw_csv_data: string
    :return: list, of CSV rows, hopefully
    """
    return csvstring2dict(raw_csv_data)


def graph(state=None):
    """
    controller for dealing with an uploaded file or change of graph state
    :param state: string
    :return: flask response
    """
    # Iterating over a string as a file
    if state:
        logging.error(state)
        raw_csv_data = unicode(memcache.get(str(session['sid'])))
        memcache.set(make_cache_key(session['sid'], 'raw'), raw_csv_data, 600)
        if not raw_csv_data:
            return render_template(
                'graph.html',
                error='Your session has ended, please <a href="/">upload your provider report again</a>.')
        tmp_csv = []
        rows = raw_csv_data.split("\n")
        first_row = True
        for row in rows:
            if first_row:
                first_row = False
                tmp_csv.append(row)
                continue
            if state == 'SUCCESSFUL':
                if ',SUCCESSFUL,' in row:
                    tmp_csv.append(row)
            elif state == 'UNSUCCESSFUL':
                if ',UNSUCCESSFUL,' in row:
                    tmp_csv.append(row)
            elif state == 'CANCELLED':
                if ',CANCELLED,' in row:
                    tmp_csv.append(row)
            elif state == 'FUTURE':
                if ',FUTURE,' in row:
                    tmp_csv.append(row)
        if len(tmp_csv):
            raw_csv_data = "\n".join(tmp_csv)
            logging.error(raw_csv_data)
    else:
        raw_csv_data = unicode(memcache.get(make_cache_key(session['sid'], 'raw')))
        if request.files:
            logging.error('got a file to process')
            raw_csv_data = unicode("")
            for data in request.files['csv_upload'].read():
                raw_csv_data += data
        memcache.set(make_cache_key(session['sid'], 'raw'), raw_csv_data, 600)

    return render_template(
        'graph.html',
        csv_len=len(raw_csv_data.split("\n")),
        raw_csv_data=raw_csv_data)


def warmup():
    """
    App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
    """
    return ''
