from flask import request
from yradio import add_playlist, get_yradio_uid, get_auth_token

import requests


@app.route('/create', methods=['POST'])
def create_playlist():
    yradio_uid = get_yradio_uid()
    auth_token = get_auth_token()

    args = request.get_json()
    link = args['link']
    user = args['user']
    user_id = args['spotify_id']
    tags = args['tags']

    playlist_id = link[-22:]
    response = requests.get(
        "https://api.spotify.com/v1/users/{0}/playlists/{1}".format(user_id, playlist_id),
        headers = {'Authorization': 'Bearer {0}'.format(access_token)}
    )
    #TODO handle failure
    playlist = response.body.json()
    tags = tags + get_song_tags(link)

    imported_pl = import_playlist(yradio_uid, playlist)

    add_playlist(name, user, imported_pl, tags)


#iterate through tracks gathering song information, and tagging playlist accordingly
def get_song_tags(playlist):
    tags = []
    potential_tags = []

    tracks = playlist['tracks']['items']
    for track in tracks:
        response = requests.get(
            'https://api.spotify.com/v1/audio-features/{0}'.format(track['id']),
            headers = {'Authorization': 'Bearer {0}'.format(access_token)}
        )
        features = response.body.json()
        traits = []
        if features['acousticness'] > .6:
            traits.append('acoustic')
        if features['danceability'] > .6:
            traits.append('dancy')
        if features['energy'] > .6:
            traits.append('energetic')
        if features['instrumentalness'] > .6:
            traits.append('instrumental')
        if features['liveness'] > .8:
            traits.append('liverecording')

        traits.append(track['artists'][0])
        genre = artist.get('genres', [None])[0]
        if genre:
            traits.append(genre)

        for trait in traits:
            if trait in potential_tags:
                potential_tags[trait] += 1
            else:
                potential_tags[trait] = 1

    for tag, count in potential_tags.iteritems():
        if count > len(tracks)/3:
            tags.append(tag)

    return tags

#creates new playlist, adds tracks to it, and returns the new playlist's link
def import_playlist(uid, playlist):
    response = requests.post(
        'https://api.spotify.com/v1/users/{0}/playlists'.format(uid),
        headers = {
            'Authorization': 'Bearer {0}'.format(access_token)
            'Content-Type': 'application/json'
        },
        data = {'name': playlist['name'], 'public': True}
    )

    imported_playlist = response.body.json()
    playlist_id = imported_playlist['id']

    uris = []
    for track in playlist['tracks']['items']:
        uris.append(track['uri'])

    response = requests.post(
        'https://api.spotify.com/v1/users/{0}/playlists/{1}/tracks'.format(uid, playlist_id)
        headers = {
            'Authorization': 'Bearer {0}'.format(access_token)
            'Content-Type': 'application/json'
        },
        data = {'uris': uris}
    )

    return imported_playlist['external_urls']['spotify']
