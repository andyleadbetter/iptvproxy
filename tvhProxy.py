from gevent import monkey; monkey.patch_all()

import time
import os
import requests
from gevent.pywsgi import WSGIServer
from flask import Flask, Response, request, jsonify, abort

app = Flask(__name__)

# URL format: <protocol>://<username>:<password>@<hostname>:<port>, example: https://test:1234@localhost:9981
config = {
    'bindAddr': os.environ.get('TVH_BINDADDR') or '0.0.0.0',
    'tvhURL': os.environ.get('TVH_URL'), 
    'tvhProxyURL': os.environ.get('TVH_PROXY_URL'), 
    'tunerCount': os.environ.get('TVH_TUNER_COUNT') or 1,  # number of tuners in tvh
    'tvhWeight': os.environ.get('TVH_WEIGHT') or 300,  # subscription priority
    'chunkSize': os.environ.get('TVH_CHUNK_SIZE') or 1024*1024,  # usually you don't need to edit this
    'username' : os.environ.get('TV_USERNAME'), 
    'password' : os.environ.get('TV_USERNAME') 
}


@app.route('/discover.json')
def discover():
    return jsonify({
        'FriendlyName': 'tvhProxy',
        'ModelNumber': 'HDTC-2US',
        'FirmwareName': 'hdhomeruntc_atsc',
        'TunerCount': int(config['tunerCount']),
        'FirmwareVersion': '20150826',
        'DeviceID': '52345690',
        'DeviceAuth': 'test1234',
        'BaseURL': '%s' % config['tvhProxyURL'],
        'LineupURL': '%s/lineup.json' % config['tvhProxyURL']
    })


@app.route('/lineup_status.json')
def status():
    return jsonify({
        'ScanInProgress': 0,
        'ScanPossible': 1,
        'Source': "Cable",
        'SourceList': ['Cable']
    })


@app.route('/lineup.json')
def lineup():	
    lineup = []

    for c in _get_channels():
            url = 'http://meowyapmeow.com:8080/live/%s/%s/%s.ts' % ( config['username'], config['password'], c['stream_id'])

            lineup.append({'GuideNumber': str(c['num']),
                           'GuideName': c['name'],
                           'URL': url
                           })

    return jsonify(lineup)


@app.route('/lineup.post')
def lineup_post():
    return ''

@app.route('/epg.xmltv')
def tvguide():
    
    tvguide = ''

    return tvguide


def _get_channels():
    url = '%s&action=get_live_streams' % config['tvhURL']

    try:
        r = requests.get(url)
        return r.json()

    except Exception as e:
        print('An error occured: ' + repr(e))


if __name__ == '__main__':
    http = WSGIServer((config['bindAddr'], 5005), app.wsgi_app)
    http.serve_forever()
