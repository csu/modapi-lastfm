from threading import Thread

from flask import Blueprint, jsonify
import requests

from common import require_secret
from config import config
import secrets

module = Blueprint(config['module_name'], __name__)

def perform_scrobbles_backup():
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
    notifier.quick_send('Backed up %s Last.fm scrobbles.' % len(items))

@module.route('/backup')
@module.route('/backup/')
@require_secret
def backup_all_scrobbles():
    t = Thread(target=perform_scrobbles_backup, args=[])
    t.start()

    return jsonify({
        'status': 'started'
    })