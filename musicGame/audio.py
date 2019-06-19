#
# musicGame/audio.py
# by William Neild
#

import os
import sys
import time
import threading

from musicGame.game import format_songname



class Player:
    """
    The main class which handles audio playing and some conversion
    """

    def play(self, song, duriation):
        """
        function that is initially called to play some audio

        first it checks whether a song file is availible, then 
        it checks whether a "Player" thread is already running
        and if it isn't, creates a new one to start playing the
        specified audio clip
        """

        if song.location is not None:
            for thread in threading.enumerate():
                if thread.name == "Player":
                    running = True
                else:
                    running = False
            
            if not running:
                play_thread = threading.Thread(target=self.play_check, name="Player", args=(song, duriation))
                play_thread.daemon = True
                play_thread.start()

    def play_check(self, song, duriation):
        if sys.platform == "darwin":
            self.play_mac(song, duriation)
        else:
            self.play_other(song, duriation)

    def play_mac(self, song, duriation):
        import subprocess

        # use mac specific afplay command
        try:
            mac_process = subprocess.Popen([ "afplay", song.location ])
            mac_process.wait(duriation)
        except subprocess.TimeoutExpired as error:
            print("Song stopped")
        except Exception as error:
            print(f"Unknown Error: {error}")
        finally:
            mac_process.terminate()
            mac_process.kill()

    def play_other(self, song, duriation):
        import multiprocessing
        import playsound as ps

        # placed here as only windoes seems affected by this bug
        self.convert_id3v23(song.location)

        # use playsound inside of a subprocess as you are unable to control it via
        # the playsound module
        audio_process = multiprocessing.Process(target=ps.playsound, args=(song.location, ))
        
        try:
            audio_process.start()
            audio_process.join(duriation)
            print("Song Stopped")
        except Exception as e:
            print(e)

        # ensure that the process is no longer running
        if audio_process.is_alive():
            audio_process.terminate()
            audio_process.join()
    
    def convert_id3v23(self, file):
        """
        By default, files downloaded from spotify use the id3v2.4 tag
        format which doesn't work with playsound on windows (unsure
        about Linux)
        """
        
        from mutagen.id3 import ID3

        audio_file = ID3(file)
        audio_file.save(v2_version=3)



class Song:
    """
    This object handles an song location and most of it's
    small amount of required data
    """

    def __init__(self, id = None, name=None, artists=None, location=None, url=None):
        self.id = id
        self.name = format_songname(name)
        self.artists = " & ".join(artists)
        self.location = location
        self.url = url
