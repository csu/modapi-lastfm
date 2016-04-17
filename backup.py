import requests

import secrets

def perform_scrobbles_backup(send_notification, uploader, notifier):
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