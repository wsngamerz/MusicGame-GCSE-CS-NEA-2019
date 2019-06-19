#
# musicGame/game.py
# by William Neild
# 

"""
The game file should contain all functions of the game and
the application that do not fit into the database, audio, 
networking or gui class such as logging in and other helper
functions.
"""

from musicGame.database import db_session, User, Result
from musicGame.networking import Spotify, Downloader

from sqlalchemy import desc

# This initiates the spotify class
# Done here because this is the only 
# place where it should be accessed
spotify = Spotify()



def login(username, password):
    """
    Login function does what it sounds like it does,
    it logs in the user by first querying the database
    and then comparing the username and passwords.
    
    Args:
        username: The username to query
        password: The password to check
    
    Returns:
        Success:
            returns a user dictionary that contains 
            basic info such as their name
        Error:
            returns False
    """
    
    user = db_session.query(User).filter(User.username == username).first()
    
    if user is None:
        return False
    else:
        if user.password == password:
            return {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        else:
            return False




def register(username, password, password_confirmation, first_name, last_name):
    """
    Register a new user and validates whether the user is
    allowed to register by first having to pass a number of
    checks such as blank username/password, checking both
    password entries are equal

    Examples:
        >>> register("wneild5", "password", "password", "William", "Neild")
        True

        >>> register("wneild5", "password", "notTheSamePassword", "William", "Neild")
        ["Passwords don't match"]

    Args:
        username: The username to register
        password: The password for the user
        password_confirmation: To check the password is correct
        first_name: First name of the user
        last_name: Last name of the user
    
    Return:
        if the user registration passes all of the checks, True is
        returned but if it fails one or more checks, a list holding
        the error strings is returned
    """

    # empty errors array to hold
    errors = []

    if username == "":
        errors.append("Username is blank")
    
    if password == "":
        errors.append("Password is blank")
    
    if not password == password_confirmation:
        errors.append("Passwords don't match")
    
    # check for user already existing
    user_check = db_session.query(User).filter_by(username=username).first()
    if user_check is not None:
        errors.append("Username already in use")

    if len(errors) == 0:
        user = User(username=username, password=password,first_name=first_name, last_name=last_name)
        db_session.add(user)
        db_session.commit()
        return True
    else:
        return errors



def save_result(user_id, total_score, correct_guesses, incorrect_guesses):
    from sqlalchemy.orm import sessionmaker, scoped_session
    from musicGame.database import db_engine

    session_factory = sessionmaker(bind=db_engine)
    Session = scoped_session(session_factory)
    db_session = Session()

    new_result = Result(user_id=user_id, score=total_score, questions_correct=correct_guesses, questions_incorrect=incorrect_guesses)
    db_session.add(new_result)
    db_session.commit()



def get_results(user_id):
    from sqlalchemy.orm import sessionmaker, scoped_session
    from musicGame.database import db_engine

    session_factory = sessionmaker(bind=db_engine)
    Session = scoped_session(session_factory)
    db_session = Session()

    user_results = db_session.query(Result).filter_by(user_id=user_id).all()
    
    return user_results




def format_songname(song_name):
    """
    Basic function to nicely format song names from
    the Spotify API (or anywhere else that doesn't 
    provide nicely foRmATTeD nAmES LIKE THEY SHOULD)

    Removes:
        - Brackets      e.g: '(feat. artist)' or '(with artist)'
        - Remix String  e.g: ' - artist remix'
        - Feat. String  e.g: 'feat. artist'
        - Radio Edit    'radio edit'
        - Dash          ' - '
        - Remastered    'remastered'
        - Remix         '[remix]'
        - Film Version  'film version'
        - Dots          '.'
        - Spiderverse   'spider-man: into the spider-verse' <-- This is a real pain
    
    Args:
        song_name: The song name string to perform the formatting on
    
    Returns:
        returns a string which has been formated by removing as much
        of the useless information out of the song title which shouldn't
        realy be there in the first place.
    """

    song_name = song_name.lower()
    
    # Remove brackets from the string

    num_brackets = song_name.count("(")

    for bracket_pairs in range(num_brackets):
        bracket_start = song_name.find("(")
        bracket_end = song_name.find(")")

        if bracket_start != -1 and bracket_end != -1:
            song_name = song_name.replace(song_name[bracket_start:bracket_end + 1], "")

    # Remove common remix string

    remix_start = song_name.find(" - ")
    remix_end = song_name.find("remix")

    if remix_start != -1 and remix_end != -1:
        song_name = song_name.replace(song_name[remix_start:remix_end + 5], "")


    # Remove feat out of brackets string

    feat_start = song_name.find("feat.")

    if feat_start != -1:
        song_name = song_name.replace(song_name[feat_start: ], "")

    # List of basic 'from -> to' values to remove

    terms = [
        ("radio edit", ""),
        (" - ", " "),
        (",", " "),
        ("remastered", ""),
        ("[remix]", ""),
        ("film version", ""),
        (".", ""),
        ("spider-man: into the spider-verse", ""),
        ("from \"watership down\"", "")
    ]

    for term in terms:
        song_name = song_name.replace(term[0], term[1])

    # this should fix double spaces which mess up if the user
    # doesnt guess with an exta space
    return " ".join(song_name.split())



def blank_songname(song_name):
    """
    This function convers a full song name which has already been formated to
    look pretty to its 'to guess' form:

    Example:
        viva la vida                  -> V--- L- V---
        sandstorm                     -> S-------
        harder better faster stronger -> H----- B----- F----- S-------
    
    Args:
        song_name: The song string to convert
    
    Returns:
        returns a string of the song name thats ready to be guessed
    """

    word_list = song_name.split(" ")
    song_guess = []
    
    for word in word_list:
        word_guess = ""
        had_first = False
        
        for char in word:
            if char.isalpha():
                if not had_first:
                    word_guess += char.upper()
                    had_first = True
                else:
                    word_guess += "_ "
            else:
                word_guess += char

        song_guess.append(word_guess)

    return " ".join(song_guess)



def load_playlist(playlist_id="37i9dQZF1DXcBWIGoYBM5M"):
    from musicGame.audio import Song

    """
    This function gets the playlist from spotify and returns
    a list of Audio objects which can be played in the music
    Player.

    Good Playlists:
        37i9dQZF1DXcBWIGoYBM5M -> 40 songs   -> Official UK Top 40 [Default Playlist]
        5MN1X3chNX5Dxk8Pav3Dtu -> 500+ songs -> Now thats what i call music 90 - present version
        37i9dQZF1DX0Yxoavh5qJV -> 80+ songs  -> Spotify: Christmas Hits
        37i9dQZF1DXcBWIGoYBM5M -> 50+ songs  -> Spotify: Today's Top Hits
    """

    game_playlist = spotify.get_playlist(playlist_id)

    playlist_song_list = [song["track"] for song in game_playlist["tracks"]["items"]]
    song_list = []

    for song in playlist_song_list:
        artist_list = [artist["name"] for artist in song["album"]["artists"]]
        song_id = song["id"]
        url = song["preview_url"]
        song_object = Song(id = song_id, name = song["name"], artists = artist_list, url = url)
        song_list.append(song_object)
    
    # Download all songs to the assets directory
    downloader = Downloader(8)
    downloader.start(song_list)
    
    return song_list
