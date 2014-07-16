# coding=utf-8
"""
views.py

View handlers for login, home and warmup
"""
import StringIO
import csv
from google.appengine.api import users
from flask import url_for, redirect, render_template, request, jsonify
from flask import request


HELPOUT_NAME = 0
PROVIDER_NAME = 1
PAST_FUTURE = 2
# 'PAST' or 'FUTURE'
SESSION_STATE = 3
# 'SUCCESSFUL', UNSUCCESSFUL', 'CANCELLED'
EXPECTED_DURATION = 4
# '30' or '45' etc, minutes
ACTUAL_DURATION = 5
# '0' if cancelled/unsuccessful, else '38' etc
SESSION_START_PST = 6
# YYYY-MM-DD HH:MM:SS in PST
EARNINGS = 7
# '0.0' if free, else '25.0' for $25, etc
INSTANT_OR_SCHEDULED = 8
# 'INSTANT' or 'SCHEDULED'
PROVIDER_DEVICE = 9
# 'DESKTOP', 'MOBILE_ANDROID', 'DESKTOP:MOBILE_ANDROID', 'MOBILE_IOS', 'DESKTOP:MOBILE_IOS'
CONSUMER_DEVICE = 10
# 'DESKTOP', 'MOBILE_ANDROID', 'DESKTOP:MOBILE_ANDROID', 'MOBILE_IOS', 'DESKTOP:MOBILE_IOS'
PROVIDER_NO_SHOW = 11
# 'true' or 'false'
CONSUMER_NO_SHOW = 12
# '0' or '1'
PROVIDER_JOINED_PST = 13
# YYYY-MM-DD HH:MM:SS in PST
CONSUMER_JOINED_PST = 14
# YYYY-MM-DD HH:MM:SS in PST
RATING = 15
# '0' if unsuccessful or no rating left yet
FEEDBACK_COMMENTS = 16
# string, may be blank if only a star rating given


def login():  # pragma: no cover
    """
    user login
    """
    guser = users.get_current_user()

    if not guser:
        return redirect(users.create_login_url(url_for('home')))

    return redirect(users.create_login_url(url_for('home')))


def home():  # pragma: no cover
    """
    redirect user appropriately
    """
    return render_template('index.html')


def graph():
    # Iterating over a string as a file
    string_reader = csv.reader(StringIO.StringIO(request.files['csv_upload'].read()))
    payload = []

    successful_sessions = []
    unsuccessful_sessions = []
    cancelled_sessions = []
    state_other_sessions = []

    paid_sessions = []
    free_sessions = []
    total_earnings = 0
    avg_earnings = 0

    successful_session_names = {}
    unsuccessful_session_names = {}
    cancelled_session_names = {}
    other_session_names = {}

    minutes_spent = {}

    skip_header_row = True
    for row in string_reader:
        if skip_header_row or row[PAST_FUTURE] == 'FUTURE':
            skip_header_row = False
            continue

        helpout_name = unicode(row[HELPOUT_NAME])
        if helpout_name not in successful_session_names:
            successful_session_names[helpout_name] = 0
        if helpout_name not in unsuccessful_session_names:
            unsuccessful_session_names[helpout_name] = 0
        if helpout_name not in cancelled_session_names:
            cancelled_session_names[helpout_name] = 0
        if helpout_name not in other_session_names:
            other_session_names[helpout_name] = 0
        if helpout_name not in minutes_spent:
            minutes_spent[helpout_name] = {
                'session_lengths': [],
                'total_duration': 0,
                'avg_duration': 0,
                'total_sessions': 0,
            }

        if row[SESSION_STATE] == 'SUCCESSFUL':
            successful_sessions.append(row)

            successful_session_names[helpout_name] += 1

            exp_dur = int(row[EXPECTED_DURATION])
            suc_sessions = successful_session_names[helpout_name]

            minutes_spent[helpout_name]['session_lengths'].append(int(row[EXPECTED_DURATION]))
            minutes_spent[helpout_name]['total_duration'] += int(row[ACTUAL_DURATION])
            minutes_spent[helpout_name]['total_sessions'] = successful_session_names[helpout_name]
            minutes_spent[helpout_name]['avg_duration'] = \
                float(minutes_spent[helpout_name]['total_duration'] / successful_session_names[helpout_name])
            minutes_spent[helpout_name]['session_length_avg'] = \
                sum(minutes_spent[helpout_name]['session_lengths']) / suc_sessions

            if row[EARNINGS] == '0.0':
                free_sessions.append(row)
            elif row[EARNINGS]:
                paid_sessions.append(row)
                total_earnings += float(row[EARNINGS])
                avg_earnings = float(total_earnings / len(paid_sessions))

        elif row[SESSION_STATE] == 'UNSUCCESSFUL':
            unsuccessful_sessions.append(row)
            unsuccessful_session_names[helpout_name] += 1

        elif row[SESSION_STATE] == 'CANCELLED':
            cancelled_sessions.append(row)
            cancelled_session_names[helpout_name] += 1

        elif row[SESSION_STATE]:
            state_other_sessions.append(row)
            other_session_names[helpout_name] += 1

        payload.append(row)

    return jsonify({
        'session_count': len(payload),
        #'data': payload,
        'total_earnings': total_earnings,
        'avg_earnings': avg_earnings,
        'paid_sessions': len(paid_sessions),
        'free_sessions': len(free_sessions),
        'successful_sessions': successful_session_names,
        'successful_sessions_count': len(successful_sessions),
        'unsuccessful_sessions': unsuccessful_session_names,
        'unsuccessful_sessions_count': len(unsuccessful_sessions),
        'cancelled_sessions': cancelled_session_names,
        'cancelled_sessions_count': len(cancelled_sessions),
        'other_sessions': other_session_names,
        'other_sessions_count': len(state_other_sessions),
        'minutes_spent': minutes_spent,
    })

    # keys = upload_files.keys()
    # imageurls = []
    # for key in keys:
    #     if key.find("uploadimage")!=-1:
    #          image=upload_files[key]
    #          file_name=files.blobstore.create(mime_type='image/jpg')
    #          with files.open(file_name,'a') as f:
    #               f.write(image.value)
    #          files.finalize(file_name)
    #          blob_key=files.blobstore.get_blob_key(file_name)
    #          imageurls.append(images.get_serving_url(blob_key))
    # context={}
    # context['imagelinks']=imageurls
    # self.response.write(json.dumps(context))
    # return 'graph goes here'


def warmup():
    """
    App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
    """
    return ''
