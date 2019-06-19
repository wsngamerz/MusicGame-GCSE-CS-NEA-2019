#
# musicGame/__init__.py
# by William Neild
#

"""
This section links together most of the different parts
of the game including networking and the GUI
"""


class MainGame:    
    def start(self):
        # import here so when new process is spawned
        # it shouldnt start a new gui
        from musicGame.gui import app

        app.mainloop()
