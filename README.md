# Music Game

This game tests your knowlage of the UK Top 40 through a hangman-like experience.

This game was created for the GCSE Computer Science NEA for 2019 (yes the one which was required to do but was worth 0 marks).

### Running the game

firstly, you need to install the python modules required

to do this, open the command line / terminal in this directory and run the command:

```
pip install -r requirements.txt
```

ALSO, Please create a folder called ``` assets ``` at the same directory file as the ``` start.py ``` file (didn't have time to fix the bugs :( )

Secondly, get a spotify dev account, create an application and then create a file named ``` config.json ``` with the contents:

```
{
    "client_id": "<SPOTIFY_CLIENT_ID>",
    "client_secret": "<SPOTIFY_CLIENT_SECRET>"
}
```

after that, run the python file ``` start.py ```
