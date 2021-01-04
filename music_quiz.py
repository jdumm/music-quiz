import sys
from math import log, exp
from time import time
from random import randint, shuffle, choice
from collections import deque

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def music_quiz(playlist_candidates=None, exclude_saved=False, exclude_top=False):
    """
    Start the music quiz!
    :param playlist_candidates: Option to provide list of playlist names for quiz to use
    :param exclude_saved: Don't do quiz on Liked (Saved) Songs, which are not technically a playlist
    :param exclude_top: Don't do quiz on Top Songs, which are not technically a playlist either
    :return: None
    """

    # Authenticate with proper scopes
    scope = "user-read-playback-state,user-modify-playback-state,playlist-read-private," \
            "user-library-read,user-top-read"
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))

    playlists = sp.current_user_playlists()['items']

    if playlist_candidates is not None:
        playlists = [pl for pl in playlists if pl['name'] in playlist_candidates]

    while True:
        idx = randint(-2, len(playlists) - 1)
        if idx == -1 and exclude_saved:
            continue
        if idx == -2 and exclude_top:
            continue
        break
    if 0 <= idx < len(playlists):  # Select a playlist
        pl_uri = playlists[idx]['uri']
        playlist_name = playlists[idx]['name']
        playlist = sp.playlist(pl_uri)
        tracks = playlist['tracks']['items']
    elif idx == -1:  # Select Saved Songs, which behave a bit different than a playlist
        # Little trick to get 99 tracks instead of 50:
        saved_0to49 = sp.current_user_saved_tracks(limit=50, offset=0)
        saved_49to98 = sp.current_user_saved_tracks(limit=50, offset=49)
        # 1st item in 2nd list is a repeat
        tracks = saved_0to49['items'] + saved_49to98['items'][1:]
        playlist_name = 'Liked Songs'
    else:  # idx == -2
        # Little trick to get 99 tracks instead of 50:
        top_0to49 = sp.current_user_top_tracks(limit=50, offset=0)
        top_49to98 = sp.current_user_top_tracks(limit=50, offset=49)
        # 1st item in 2nd list is a repeat
        # This list needs to be packed one layer deeper for uniformity
        tracks = [{'track': t} for t in top_0to49['items'] + top_49to98['items'][1:]]
        playlist_name = 'Top Tracks'

    print(f"Testing knowledge of playlist \'{playlist_name}\'")

    tot_points = 0
    cumu_time = 0
    points_to_win = 50
    prev_names = deque(maxlen=int(len(tracks) * 2 / 3))  # Don't repeat until 2/3 have been played
    while True:
        right_track = choice(tracks)['track']
        # right_name = right_track['name'] + ' - ' + right_track['artists'][0]['name']
        right_name = right_track['name'] + ' - ' + \
            ", ".join([a['name'] for a in right_track['artists']])
        if right_name in prev_names:
            continue
        prev_names.append(right_name)

        # TODO: Catch error about No Device here?
        sp.start_playback(uris=[right_track['uri']])

        # TODO: Selecting multiple choice from same artists could up the difficulty!
        # Stub code for randomly selecting 'wrong' track candidates from the same artist:
        # artist_uri = right_track['artists'][0]['uri']
        # tt = sp.artist_top_tracks(artist_uri)

        # Randomly select 'wrong' tracks from the same playlist
        choices = [right_name]
        con_count = 0
        num_choices = 4
        while len(choices) < num_choices:
            # name_to_add = tt['items'][i]['name']
            track = choice(tracks)['track']
            name_to_add = track['name'] + ' - ' + ", ".join([a['name'] for a in track['artists']])

            if name_to_add in choices:
                con_count += 1
                if con_count < 10:  # Give up and accept duplicate choices
                    continue
            choices.append(name_to_add)
        shuffle(choices)

        prompt = f'''
What is currently playing?
    1) {choices[0]}
    2) {choices[1]}
    3) {choices[2]}
    4) {choices[3]}
Enter number: '''
        try:
            start = time()
            guess = int(input(prompt))
            end = time()
            if not 1 <= guess <= num_choices:
                raise ValueError()
        except ValueError:
            print('Please input an integer, 1 through 4')
            sys.exit()

        delay = end - start
        cumu_time += delay
        if choices[guess - 1] == right_name:
            points = 10 / log(max(exp(1), delay))
            tot_points += points
            print(f"That's right!  It took {delay:0.2f} seconds.  {points:0.2f} points!")
        else:
            print(f"Sorry, the correct answer was {right_name}!  0 points.")

        print(f"Points so far: {tot_points:0.2f}")
        if tot_points >= points_to_win:
            print(f"\nCongrats, you got more than {points_to_win} points in a total listening "
                  f"time of {cumu_time:0.2f} seconds!")
            break


if __name__ == '__main__':
    candidate_playlists = ['Discover Weekly', 'Liked from Radio']
    # candidate_playlists = ['Bday']
    music_quiz(playlist_candidates=candidate_playlists,
               exclude_saved=False,
               exclude_top=False
               )
