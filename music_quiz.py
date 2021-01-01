import os
import sys
from random import randint, shuffle

import spotipy
from spotipy.oauth2 import SpotifyOAuth

def music_quiz():
    """
    Start the music quiz!
    """

    # Authenticate with proper scopes
    username = os.environ['USERNAME']
    scope = "user-read-playback-state,user-modify-playback-state"  # ,user-top-read
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    cur_play = sp.currently_playing()
    right_name = cur_play['item']['name']
    artist_uri = cur_play['item']['artists'][0]['uri']

    #limit = 50
    #tt = sp.current_user_top_tracks(limit=limit)
    tt = sp.artist_top_tracks(artist_uri)
    #print([t['name'] for t in tt['tracks']])
    limit = len(tt['tracks'])

    choices = [right_name]
    con_count = 0
    while len(choices) < 3:
        i = randint(0, limit-1)
        #name_to_add = tt['items'][i]['name']
        name_to_add = tt['tracks'][i]['name']
        if name_to_add in choices:
            con_count += 1
            if con_count < 10:  # Give up, accept duplicate choices
                continue
        choices.append(name_to_add)
    shuffle(choices)

    prompt = f'''
What is currently playing?
    1) {choices[0]}
    2) {choices[1]}
    3) {choices[2]}
Enter number: '''
    try:
        guess = int(input(prompt))
    except ValueError:
        print('Please input integer')
        sys.exit()

    if choices[guess-1] == right_name:
        print("That's right, you win!")
    else:
        print("You lose!")


if __name__ == '__main__':
    music_quiz()
