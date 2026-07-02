#!/usr/bin/env python3
"""Investiga si Places API devuelve reviews de consumidores"""
import json, urllib.request, ssl, sys
sys.path.insert(0, '/home/dorti/neo-jarvis/briefing/lead-gen')

# Import key from existing scraper
from places_scraper import API_KEY as PLACES_KEY

API_URL = 'https://places.googleapis.com/v1/places:searchText'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

params = {'textQuery': 'restaurantes en Madrid', 'maxResultCount': 2}
data = json.dumps(params).encode()
req = urllib.request.Request(API_URL, data=data, headers={
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': PLACES_KEY,
    'X-Goog-FieldMask': 'places.displayName,places.websiteUri,places.internationalPhoneNumber,places.reviews,nextPageToken',
})
resp = urllib.request.urlopen(req, timeout=15)
result = json.loads(resp.read())
places = result.get('places', [])

print(f'Total places devueltos: {len(places)}')
for p in places[:2]:
    name = p.get('displayName', {}).get('text', '?')
    reviews = p.get('reviews', [])
    print(f'\n📍 {name}')
    print(f'  Reviews: {len(reviews)}')
    if reviews:
        for r in reviews[:5]:
            author = r.get('authorAttribution', {}).get('displayName', '?')
            rating = r.get('rating', '?')
            text = r.get('text', {}).get('text', '')[:120]
            uri = r.get('authorAttribution', {}).get('uri', '')
            print(f'  [{rating}⭐] {author}')
            if uri: print(f'         Perfil: {uri}')
            print(f'         "{text}"')
