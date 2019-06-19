#
# musicGame/gui.py
# by William Neild
#

from tkinter import *
from tkinter.ttk import *
from tkinter.font import Font

from threading import Timer

from musicGame.game import login, register, load_playlist, blank_songname, save_result, get_results
from musicGame.audio import Player


# #
# # Style Classes
# #

# use classes to store commonly used pieces of info



class Sizes:
    no_padding = 0
    padding = 2
    entry_padding = 1



class Cursor:
    hover = "hand2"



class Colours:
    blue = "#03A9F4"
    blue_dark = "#039BE5"
    blue_grey = "#607D8B"
    green = "#4CAF50"
    red = "#F44336"
    white = "#FFFFFF"



class Application(Frame):
    """
    The main GUI class
	
	This holds all of the logic to draw the UI
	"""

    def __init__(self, master=None):
        print("=" * 20)
        print(" Started Music Game ")
        print("=" * 20)

        super().__init__(master)
        self.root = master
        self.grid(row=0, column=0, sticky="nsew")

        # setup the audio player
        self.player = Player()

        # how long in seconds the song will play for
        # if the user is correct / incorrect
        self.screen_duriation = 6
        self.no_song_decrease_multiplier = 3

        # GUI / Game State
        self.state = {
            "logged_in": False,
            "user": {
                "id": 0,
                "username": "",
                "first_name": "",
                "last_name": ""
            },
            "songs": {
                "current_song": None,
                "songs_list": []
            },
            "game": {
                "attempts": 0,
                "total_score": 0,
                "total_correct": 0,
                "total_incorrect": 0
            }
        }

		# Setup some fonts
        self.font_default = Font(family="Helvetica", size=12)
        self.font_title = Font(family="Helvetica", size=20, weight="bold")
        self.font_subtitle = Font(family="Helvetica", size=14)
        self.font_guess = Font(family="Helvetica", size=20)

        # Styles
        self.style = Style(self.root)
        self.style.theme_use("classic")
        self.style.configure("Incorrect.TLabel", background=Colours.red, foreground=Colours.white)
        self.style.configure("Correct.TLabel", background=Colours.green, foreground=Colours.white)
        self.style.configure("MusicGame.TLabel", background=Colours.blue_grey, foreground=Colours.white)
        self.style.configure("MusicGame.TButton", background=Colours.blue, foreground=Colours.white, borderwidth=0, relief='flat', padding=0, highlightthickness=0)
        self.style.map("MusicGame.TButton", background=[("active", Colours.blue_dark)])
        self.style.configure("MusicGame.TEntry", background=Colours.white, borderwidth=0, relief='flat', padding=0, highlightthickness=0)

        # Show the loading page while playlists and audio files are being downloaded
        self.loading_page()

        # After that, show the main page
        self.main_page()
    
    # #
    # # Some utility functions
    # #

    def guess(self, song, guess):
        # increase attempts straight away
        attempts = self.state["game"]["attempts"] + 1
        score = self.state["game"]["total_score"]

        # update the attempts state
        self.state["game"]["attempts"] = attempts

        if song.name.lower() == guess.lower():

            # add points
            if attempts == 1:
                score += 3
            elif attempts == 2:
                score += 1

            # update the score state
            self.state["game"]["total_score"] = score

            self.state["game"]["total_correct"] = self.state["game"]["total_correct"] + 1
            self.correct_guess(song)
        else:
            self.state["game"]["total_incorrect"] = self.state["game"]["total_incorrect"] + 1
            self.incorrect_guess(song)

    def clear_screen(self, root):
        # removes all widgets from the 'root' element
        for widget in root.winfo_children():
            widget.destroy()

    def next_song(self):
        # updates the gui state
        song_id = self.state["songs"]["current_song"]
        song_id += 1

        self.state["game"]["attempts"] = 0

        try:
            self.state["songs"]["current_song"] = song_id
            self.play_page()
        except IndexError:
            print("Completed playlist")
            self.game_over("Correct.TLabel")

    def user_login(self, username, password):
        self.login_widget.withdraw()

        if username != "" and password != "":
            result = login(username, password)
            
            if result:
                self.state["logged_in"] = True
                self.state["user"] = result
                self.main_page()
            else:
                self.login_page()
            
        else:
            self.login_page()
    
    def user_register(self, username, password, password_confirmation, first_name, last_name):
        self.register_widget.withdraw()
        result = register(username, password, password_confirmation, first_name, last_name)
        
        print(result)
        
        if type(result) != list:
            self.user_login(username, password)
        else:
            self.register_page()

    # #
    # # Pages
    # #

    def main_page(self):
        self.clear_screen(self.master)

		# Show main window as it 'might' have been hidden after loading the login window
        self.root.update()
        self.root.deiconify()

        if self.state["logged_in"]:
            self.main_title = Label(text="The Music Game", font=self.font_title, style="MusicGame.TLabel")
            self.main_title.grid(row=0, columnspan=2)

            self.main_welcome_text = Label(text=f"Welcome back, {self.state['user']['first_name']}!", font=self.font_subtitle, style="MusicGame.TLabel")
            self.main_welcome_text.grid(row=1, columnspan=2)

            spacer = Label(style="MusicGame.TLabel").grid(row=2, columnspan=2)

            # Buttons
            self.button_play = Button(text="Play", width=50, command=lambda: self.play_page(), style="MusicGame.TButton", cursor=Cursor.hover)
            self.button_play.grid(row=3, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)

            self.button_results = Button(text="Results", width=50, command=self.result_page, style="MusicGame.TButton", cursor=Cursor.hover)
            self.button_results.grid(row=4, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)
            
            self.button_account = Button(text="Account", width=50, command=self.account_page, style="MusicGame.TButton", cursor=Cursor.hover)
            self.button_account.grid(row=5, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)
        else:
			# Hide the main window as the login page is in a seperate window
            self.root.withdraw()
            self.login_page()
    

    def loading_page(self):
        self.clear_screen(self.master)

        self.loading_text = Label(text="Loading", font=self.font_title, style="MusicGame.TLabel")
        self.loading_text.grid(row=0, columnspan=2, pady=25)

        self.root.update()
        
        song_playlist = load_playlist()

        self.state["songs"]["songs_list"] = song_playlist
        self.state["songs"]["current_song"] = 0
        
        self.clear_screen(self.master)


    def login_page(self):
        self.login_widget = Toplevel(padx=20, pady=5) # New Window
        self.login_widget.configure(background=Colours.blue_grey)
        self.login_widget.resizable(width=False, height=False)
        self.login_widget.title("Login")
        self.login_widget.attributes("-topmost", True) # makes sure login window at front
        self.login_widget.protocol("WM_DELETE_WINDOW", self.root.destroy) # ensures main window will be deleted if x clicked on this window

        login_title = Label(self.login_widget, text="Login", font=self.font_title, style="MusicGame.TLabel")
        login_title.grid(row=0, column=0, columnspan=2)

        #
        # Entries
        #

        # Login Entry
        login_username_text = Label(self.login_widget, text="Username", font=self.font_default, style="MusicGame.TLabel")
        login_username_text.grid(row=1, column=0, padx=Sizes.padding, pady=Sizes.padding)
        login_username_entry = Entry(self.login_widget, style="MusicGame.TEntry")
        login_username_entry.grid(row=1, column=1, padx=Sizes.entry_padding, pady=Sizes.entry_padding, ipadx=Sizes.entry_padding, ipady=Sizes.entry_padding)

        # Password Entry
        login_password_text = Label(self.login_widget, text="Password", font=self.font_default, style="MusicGame.TLabel")
        login_password_text.grid(row=2, column=0, padx=Sizes.padding, pady=Sizes.padding)
        login_password_entry = Entry(self.login_widget, show="*", style="MusicGame.TEntry")
        login_password_entry.grid(row=2, column=1, padx=Sizes.entry_padding, pady=Sizes.entry_padding, ipadx=Sizes.entry_padding, ipady=Sizes.entry_padding)

        spacer = Label(style="MusicGame.TLabel").grid(row=2, columnspan=2)

        #
        # Buttons
        #

		# Uses lambda function to make sure the command isn't ran until the button is clicked
        login_button = Button(self.login_widget, width=25, text="Login", command=lambda: self.user_login(login_username_entry.get(), login_password_entry.get()), style="MusicGame.TButton", cursor=Cursor.hover)
        login_button.grid(row=3, column=0, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)

        register_button = Button(self.login_widget, width=25, text="Create an account", command=lambda: self.register_page(), style="MusicGame.TButton", cursor=Cursor.hover)
        register_button.grid(row=4, column=0, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)


    def register_page(self):
        self.register_widget = Toplevel(padx=20, pady=5) # New Window
        self.register_widget.configure(background=Colours.blue_grey)
        self.register_widget.resizable(width=False, height=False)
        self.register_widget.title("Create Account")
        self.register_widget.attributes("-topmost", True)

        register_title = Label(self.register_widget, text="Create Account", font=self.font_title, style="MusicGame.TLabel")
        register_title.grid(row=0, column=0, columnspan=2)

        #
        # Entries
        #

        # Username Entry
        register_username_text = Label(self.register_widget, text="Username:", style="MusicGame.TLabel")
        register_username_text.grid(row=1, column=0)
        register_username_entry = Entry(self.register_widget, style="MusicGame.TEntry")
        register_username_entry.grid(row=1, column=1, padx=Sizes.entry_padding, pady=Sizes.entry_padding, ipadx=Sizes.entry_padding, ipady=Sizes.entry_padding)

        # Password Entry
        register_password_text = Label(self.register_widget, text="Password:", style="MusicGame.TLabel")
        register_password_text.grid(row=2, column=0)
        register_password_entry = Entry(self.register_widget, show="*", style="MusicGame.TEntry")
        register_password_entry.grid(row=2, column=1, padx=Sizes.entry_padding, pady=Sizes.entry_padding, ipadx=Sizes.entry_padding, ipady=Sizes.entry_padding)

        # Password Confirmation Entry
        register_password_confirmation_text = Label(self.register_widget, text="Confirm Password:", style="MusicGame.TLabel")
        register_password_confirmation_text.grid(row=3, column=0)
        register_password_confirmation_entry = Entry(self.register_widget, show="*", style="MusicGame.TEntry")
        register_password_confirmation_entry.grid(row=3, column=1, padx=Sizes.entry_padding, pady=Sizes.entry_padding, ipadx=Sizes.entry_padding, ipady=Sizes.entry_padding)

        # First Name Entry
        register_first_name_text = Label(self.register_widget, text="First name:", style="MusicGame.TLabel")
        register_first_name_text.grid(row=4, column=0)
        register_first_name_entry = Entry(self.register_widget, style="MusicGame.TEntry")
        register_first_name_entry.grid(row=4, column=1, padx=Sizes.entry_padding, pady=Sizes.entry_padding, ipadx=Sizes.entry_padding, ipady=Sizes.entry_padding)

        # Last Name Entry
        register_last_name_text = Label(self.register_widget, text="Last name:", style="MusicGame.TLabel")
        register_last_name_text.grid(row=5, column=0)
        register_last_name_entry = Entry(self.register_widget, style="MusicGame.TEntry")
        register_last_name_entry.grid(row=5, column=1, padx=Sizes.entry_padding, pady=Sizes.entry_padding, ipadx=Sizes.entry_padding, ipady=Sizes.entry_padding)


        # Register Button
        register_button = Button(self.register_widget, text="Create an account", command=lambda: self.user_register(register_username_entry.get(), register_password_entry.get(), register_password_confirmation_entry.get(), register_first_name_entry.get(), register_last_name_entry.get()), style="MusicGame.TButton", cursor=Cursor.hover)
        register_button.grid(row=6, column=0, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)
    

    def play_page(self):
        self.clear_screen(self.root)

        song_id = self.state["songs"]["current_song"]
        song = self.state["songs"]["songs_list"][song_id]


        print("=" * 25)
        print(f"Song ID: { self.state['songs']['current_song'] }")
        print(f"Song Name: { song.name }")
        print(f"Song Artist: { song.artists }")
        print(f"Attempts: { self.state['game']['attempts'] }")
        print(f"Score: { self.state['game']['total_score'] }")
        print("=" * 25)


        song_name = Label(text=blank_songname(song.name), font=self.font_guess, style="MusicGame.TLabel")
        song_name.grid(row=0, column=0, columnspan=2)

        song_artist = Label(text=song.artists, font=self.font_default, style="MusicGame.TLabel")
        song_artist.grid(row=1, column=0, columnspan=2)

        spacer = Label(style="MusicGame.TLabel").grid(row=2, columnspan=2)

        guess_entry = Entry(width=41, style="MusicGame.TEntry")
        guess_entry.focus()
        guess_entry.grid(row=3, columnspan=2, padx=Sizes.no_padding, pady=Sizes.no_padding, ipadx=Sizes.entry_padding, ipady=Sizes.entry_padding)

        guess_command = lambda event: self.guess(song, guess_entry.get())
        self.root.bind("<Return>", guess_command)

        guess_button = Button(width=40, text="Make a guess:", command=lambda: guess_command(None), style="MusicGame.TButton", cursor=Cursor.hover)
        guess_button.grid(row=4, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)


    def correct_guess(self, song):
        self.clear_screen(self.master)

        correct_text = Label(text="CORRECT", style="Correct.TLabel", font=self.font_title)
        correct_text.grid(row=0, column=0, columnspan=2, padx=Sizes.padding, pady=Sizes.padding * 5, ipadx=Sizes.padding * 2, ipady=Sizes.padding * 2)

        print(song.location)

        if song.location is None:
            duriation = self.screen_duriation / self.no_song_decrease_multiplier
        else:
            duriation = self.screen_duriation

        self.player.play(song, duriation)

        # prevent next screen for 'screen_duriation' seconds
        delay = Timer(duriation, self.next_song)
        delay.start()
    
    def incorrect_guess(self, song):
        self.clear_screen(self.master)

        incorrect_text = Label(text="INCORRECT", style="Incorrect.TLabel", font=self.font_title)
        incorrect_text.grid(row=0, column=0, columnspan=2, padx=Sizes.padding, pady=Sizes.padding * 5, ipadx=Sizes.padding * 2, ipady=Sizes.padding * 2)

        attempts = self.state["game"]["attempts"]

        if song.location is None:
            duriation = self.screen_duriation / self.no_song_decrease_multiplier
        else:
            duriation = self.screen_duriation

        if attempts == 2: # replace with if was last guess
            self.player.play(song, self.screen_duriation * 2)
            delay = Timer(duriation, lambda: self.game_over("Incorrect.TLabel"))
            delay.start()
        else:
            delay = Timer(duriation, self.play_page)
            delay.start()


    def game_over(self, text_style):
        self.clear_screen(self.master)

        # Reset song counter
        self.state["songs"]["current_song"] = None

        game_over_text = Label(text="Game Over", style=text_style, font=self.font_title)
        game_over_text.grid(row=0, column=0, columnspan=2, padx=Sizes.padding, pady=Sizes.padding * 5, ipadx=Sizes.padding * 2, ipady=Sizes.padding * 2)

        total_score = Label(text=f"Your overall score was: { self.state['game']['total_score'] }.", style="MusicGame.TLabel", font=self.font_default)
        total_score.grid(row=1, column=0, columnspan=2)

        total_correct = Label(text=f"You had { self.state['game']['total_correct'] } correct guesses.", style="MusicGame.TLabel", font=self.font_default)
        total_correct.grid(row=2, column=0, columnspan=2)

        total_incorrect = Label(text=f"You had { self.state['game']['total_incorrect'] } incorrect guesses.", style="MusicGame.TLabel", font=self.font_default)
        total_incorrect.grid(row=3, column=0, columnspan=2)

        main_menu_button = Button(text="Main Menu", style="MusicGame.TButton", command=self.main_page, state=DISABLED)
        main_menu_button.grid(row=4, column=0, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)

        # Save result into database
        save_result(self.state["user"]["id"], self.state["game"]["total_score"], self.state["game"]["total_correct"], self.state["game"]["total_incorrect"])

        delay = Timer(self.screen_duriation, lambda: main_menu_button.config(state=NORMAL))
        delay.start()

    def account_page(self):
        # Debatable whether should implement
        pass

    def result_page(self):
        self.clear_screen(self.master)

        user_results = get_results(self.state["user"]["id"])
        user_results.sort(key=lambda x: x.score, reverse=True)

        results_title = Label(text="User Results", style="MusicGame.TLabel", font=self.font_title)
        results_title.grid(row=0, column=0, columnspan=2)

        result_header = Label(text="Score Correct   Questions   Incorrect Questions", style="MusicGame.TLabel", font=self.font_subtitle)
        result_header.grid(row=1, column=0, columnspan=2)

        for result in range(5):
            try:
                result_row = user_results[result]
                label_text = "{0: <30} {1: <24} {2: <40}".format(result_row.score, result_row.questions_correct, result_row.questions_incorrect)
                result_text = Label(text=label_text, style="MusicGame.TLabel", font=self.font_default)
                result_text.grid(row=result + 2, column=0, columnspan=2)
            except Exception as e:
                # Theres no point handling this error
                pass
        
        main_menu_button = Button(text="Main Menu", style="MusicGame.TButton", command=self.main_page)
        main_menu_button.grid(row=8, column=0, columnspan=2, padx=Sizes.padding, pady=Sizes.padding)



root = Tk()

root.title("Music Game")
root.geometry("480x200")
root.configure(background=Colours.blue_grey)
root.resizable(width=False, height=False)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

app = Application(master=root)
