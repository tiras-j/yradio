from flask import request

import requests
import json

#iterate through tracks gathering song information, and tagging playlist accordingly
def get_song_tags(auth_token, playlist):
    tags = []
    potential_tags = {}

    tracks = playlist['tracks']['items']

    track_ids = []
    features = []
    counter = 0
    for track in tracks:
        counter += 1
        track_ids.append(track['track']['id'])

        artist = track['track']['artists'][0]
        genre = artist.get('genres', [None])[0]

        if artist['name'] in potential_tags:
            potential_tags[artist['name']] += 1
        else:
            potential_tags[artist['name']] = 1

        if genre:
            if genre in potential_tags:
                potential_tags[genre] += 1
            else:
                potential_tags[genre] = 1

        if counter % 100 == 0:
            response = requests.get(
                'https://api.spotify.com/v1/audio-features/?ids=' + ','.join(track_ids),
                headers = {'Authorization': 'Bearer {0}'.format(auth_token)}
            )
            partial_features = response.json()['audio_features']
            features.extend(partial_features)

    traits = []
    for feature in features:
        if feature['acousticness'] > .7:
            traits.append('acoustic')
        elif feature['acousticness'] < .3:
            traits.append('electronic')
        if feature['danceability'] > .6:
            traits.append('dancy')
        if feature['energy'] > .7:
            traits.append('energetic')
        elif feature['energy'] < .3:
            traits.append('calm')
        if feature['instrumentalness'] > .6:
            traits.append('instrumental')
        if feature['liveness'] > .8:
            traits.append('liverecording')
        if feature['valence'] > .8:
            traits.append('happy')
        elif feature['valence'] < .2:
            traits.append('melancholy')

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
def import_playlist(auth_token, yradio_uid, user_id, playlist):
    data =  json.dumps({'name': playlist['name'], 'public': True})
    print data
    response = requests.post(
        'https://api.spotify.com/v1/users/{0}/playlists'.format(yradio_uid),
        headers = {
            'Authorization': 'Bearer {0}'.format(auth_token),
            'Content-Type': 'application/json'
        },
        data = data
    )

    imported_playlist = response.json()
    print playlist['name']
    print imported_playlist
    imported_playlist_id = imported_playlist['id']
    playlist_id = playlist['id']

    uris = []
    for track in playlist['tracks']['items']:
        uris.append(track['track']['uri'])

    song_index = len(uris)
    song_count = playlist['tracks']['total']
    while song_count >= song_index:
        response = requests.post(
            'https://api.spotify.com/v1/users/{0}/playlists/{1}/tracks'.format(yradio_uid, imported_playlist_id),
            headers = {
                'Authorization': 'Bearer {0}'.format(auth_token),
                'Content-Type': 'application/json'
            },
            data = json.dumps({'uris': uris})
        )
        #TODO check response code

        if song_count != song_index:
            #get more songs
            response = requests.get(
                "https://api.spotify.com/v1/users/{0}/playlists/{1}/tracks?offset={2}".format(user_id, playlist_id, song_index),
                headers = {'Authorization': 'Bearer {0}'.format(auth_token)}
            )

            tracks = response.json()['items']
            uris = []
            for track in tracks:
                uris.append(track['track']['uri'])
            song_index += len(uris)
        else:
            return imported_playlist['external_urls']['spotify']

def get_auth_token():
    f = open('auth_token.txt', 'r')
    return f.read().rstrip()

# for testing purposes
if __name__ == "__main__":
    token = get_auth_token()
    playlist = {'name': 'myname'}
    import_playlist(token, 1241941697, 213123123123, playlist)


