#!/usr/bin/env python3
"""Resolve YouTube channel IDs and fetch latest videos via RSS."""
import urllib.request
import re
from xml.etree import ElementTree as ET

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=25).read()

def get_channel_id(handle_url):
    try:
        h = fetch(handle_url).decode('utf-8', 'ignore')
        m = re.search(r'"externalId":"(UC[\w-]{22})"', h)
        if not m:
            m = re.search(r'"channelId":"(UC[\w-]{22})"', h)
        if not m:
            m = re.search(r'channel_id=(UC[\w-]{22})', h)
        return m.group(1) if m else None
    except Exception as e:
        return 'ERR: %s' % e

def fetch_feed(channel_id):
    url = 'https://www.youtube.com/feeds/videos.xml?channel_id=%s' % channel_id
    try:
        data = fetch(url)
        root = ET.fromstring(data)
        out = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.findtext('{http://www.w3.org/2005/Atom}title') or ''
            pub = entry.findtext('{http://www.w3.org/2005/Atom}published') or ''
            vid = entry.findtext('{http://www.youtube.com/xml/schemas/2015}videoId') or ''
            out.append((pub[:10], title, 'https://youtu.be/' + vid))
        return out
    except Exception as e:
        return [('ERR', str(e), '')]

channels = {
    'DotCSV': 'https://www.youtube.com/@DotCSV/videos',
    'XavierMitjana': 'https://www.youtube.com/@xaviermitjana/videos',
    'JonHernandez': 'https://www.youtube.com/@JonHernandez/videos',
    'DotCSVLab': 'https://www.youtube.com/@dotcsvlab/videos',
    'RingaTech': 'https://www.youtube.com/@RingaTech/videos',
    'VictorRobles': 'https://www.youtube.com/@victorroblesweb/videos',
}
for name, url in channels.items():
    cid = get_channel_id(url)
    print('====', name, '|', cid)
    if cid and cid.startswith('UC'):
        for pub, title, link in fetch_feed(cid):
            print(pub, '|', title, '|', link)
