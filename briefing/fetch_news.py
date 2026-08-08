#!/usr/bin/env python3
"""Fetch Google News RSS for briefing."""
import urllib.request
from xml.etree import ElementTree as ET

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=25).read()

def parse_gn(url, limit=20):
    data = fetch(url)
    root = ET.fromstring(data)
    out = []
    for item in root.findall('.//item'):
        title = item.findtext('title') or ''
        pub = item.findtext('pubDate') or ''
        src = item.find('source')
        src = src.text if src is not None and src.text else ''
        out.append((pub, src, title))
    return out[:limit]

queries = [
    ('IA-ES', 'https://news.google.com/rss/search?q=inteligencia%20artificial&hl=es&gl=ES&ceid=ES:es'),
    ('IA-EN', 'https://news.google.com/rss/search?q=artificial%20intelligence&hl=en&gl=US&ceid=US:en'),
    ('ESP', 'https://news.google.com/rss/search?q=Espa%C3%B1a%20actualidad&hl=es&gl=ES&ceid=ES:es'),
]
for name, u in queries:
    print('====', name)
    try:
        for pub, src, title in parse_gn(u):
            print(pub, '|', src, '|', title)
    except Exception as e:
        print('ERR', e)
