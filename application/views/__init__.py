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
    show the user the home page
    """
    session['sid'] = int(time.time())
    return render_template('index.html')


def csv2string(data):
    si = StringIO.StringIO()
    cw = csv.writer(si)
    cw.writerow(data)
    return si.getvalue().strip('\r\n')


def graph(state=None):
    # Iterating over a string as a file
    if state:
        logging.error(state)
        raw_csv_data = unicode(memcache.get(str(session['sid'])))
        memcache.set(str(session['sid']), raw_csv_data, 600)
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
        raw_csv_data = unicode(memcache.get(str(session['sid'])))
        if request.files:
            logging.error('got a file to process')
            raw_csv_data = unicode("")
            for data in request.files['csv_upload'].read():
                raw_csv_data += data
        memcache.set(str(session['sid']), raw_csv_data, 600)

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
