from datetime import timedelta
from threading import Thread

import arrow
from flask import Blueprint, jsonify, request
import requests

from common import require_secret
from config import config
import secrets

module = Blueprint(config['module_name'], __name__)

def perform_scrobbles_backup(send_notification):
    base_url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key=%s&user=%s&format=json' % (secrets.LASTFM_API_KEY, secrets.LASTFM_USER)

    items = []
    limit = 200
    page = 1
    while (page == 1) or int(result['recenttracks']['@attr']['page']) != int(result['recenttracks']['@attr']['totalPages']):
        url = '%s&limit=%s&page=%s' % (base_url, limit, page)
        result = requests.get(url).json()
        items += result['recenttracks']['track']
        page += 1

    uploader.quick_upload({'items': items},
        file_prefix='lastfm', folder=secrets.BACKUP_FOLDER_ID)

    if send_notification:
        notifier.quick_send('Backed up %s Last.fm scrobbles.' % len(items))

@module.route('/backup')
@module.route('/backup/')
@require_secret
def backup_all_scrobbles():
    send_notification = request.args.get('notify') is not None
    t = Thread(target=perform_scrobbles_backup, args=[send_notification])
    t.start()

    return jsonify({
        'status': 'started'
    })

def get_today_scrobble_count():
    today = arrow.now().date()
    tomorrow = today + timedelta(1)
    today_timestamp = arrow.get(today, 'US/Pacific').timestamp
    tomorrow_timestamp = arrow.get(tomorrow, 'US/Pacific').timestamp
    request_url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json&limit=5&from=%s&to=%s' % (secrets.LASTFM_USER, secrets.LASTFM_API_KEY, today_timestamp, tomorrow_timestamp)
    result = requests.get(request_url).json()
    return int(result['recenttracks']['@attr']['total'])


@module.route('/today')
@module.route('/today/')
@require_secret
def scrobbles_today():
    return jsonify({'count': get_today_scrobble_count()})


@module.route('/today/dashboard')
@module.route('/today/dashboard/')
@require_secret
def scrobbles_today_dashboard():
    count = get_today_scrobble_count()

    colors = ['#CCFF66', '#FFCC66', '#EBAD99']
    color = colors[0]
    if count > 10:
        color = colors[1]
    if count > 20:
        color = colors[2]

    return jsonify({'items': [{
        'title': 'Scrobbles Today',
        'body': count,
        'color': color
    }]})