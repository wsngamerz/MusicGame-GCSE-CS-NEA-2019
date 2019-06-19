#
# musicGame/networking.py
# by William Neild
#

import base64
import json
import os
import sys

import requests

from multiprocessing.pool import ThreadPool



class Spotify:
	def __init__(self):
		self.authenticated = False
		self.client_id = ""
		self.client_secret = ""
		self.token = None
		
		# Call this when the class is initialised so we are already
		# authenticated with the api before we need to use it!
		self.get_config()
		self.authenticate()

	def get_config(self):
		if os.path.exists("config.json"):
			config_data = None
			with open("config.json", "r") as config_file:
				config_data = json.loads(config_file.read())
				config_file.close()
			try:
				self.client_id = config_data["client_id"]
				self.client_secret = config_data["client_secret"]
			except KeyError as error:
				print("Config file bad, please fix")
				sys.exit(1)

	def authenticate(self):
		if not self.authenticated:
			
			got_token = False

			# check if we have already got a valid token saved
			if os.path.exists("token.txt"):
				token = None
				with open("token.txt") as token_file:
					token = token_file.read()
					token_file.close()
				
				if token is not None:
					# if the token exists, try to request the root url of
					#  spotify api with it
					request_headers = {
						"Authorization": f"Bearer {token}"
					}

					try:
						test_token = requests.get("https://api.spotify.com/v1", headers=request_headers)
					except requests.exceptions.RequestException as error:
						print("Check authentication error")
						print(error)
						sys.exit()
					
					token_test_response = json.loads(test_token.text)

					# if the api responds with a 400 error, its a valid token
					if token_test_response["error"]["status"] == 400:
						print("Valid Token :)")
						self.token = token
						self.authenticated = True
						got_token = True
					# if the server responds with a 401 error, its not valid
					elif token_test_response["error"]["status"] == 401:
						print("Invalid Token :(")
					# your screwed if you hit this
					else:
						print("Unknown response ¯\_(ツ)_/¯")

			if not got_token:
				# Encode the id and the secret
				auth_string = f"{self.client_id}:{self.client_secret}"
				auth_encoded = base64.b64encode(auth_string.encode()).decode()
				
				# Authenticate with spotify
				request_url = "https://accounts.spotify.com/api/token/"
				request_headers = {
					"Authorization": f"Basic {auth_encoded}"
				}

				request_data = {
					"grant_type": "client_credentials"
				}

				try:
					request_token = requests.post(request_url, headers=request_headers, data=request_data)
				except requests.exceptions.RequestException as error:
					print("Authentication requests error")
					print(error)
					sys.exit()
				
				# Save access token recieved in class and set authenticated
				request_result = json.loads(request_token.text)

				try:
					self.token = request_result["access_token"]
					self.authenticated = True

					# save the token in a file so that we might not
					# have to reauthenticate if the token is still valid
					with open("token.txt", "w") as token_file:
						token_file.write(self.token)
						token_file.close()
					
				except KeyError as error:
					print("Error In Authentication", error)
					self.authenticated = False

	def get_playlist(self, playlist_id):
		# it's quite obvious what this function does

		if self.authenticated:
			playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/"
			print(f"Requesting {playlist_url}")
			request_headers = {
				"Authorization": f"Bearer {self.token}"
			}

			try:
				request_playlist = requests.get(playlist_url, headers=request_headers)
			except requests.exceptions.RequestException as error:
				print("Playlist request error")
				print(error)
				sys.exit()
			
			request_playlist_result = json.loads(request_playlist.text)

			total_tracks = request_playlist_result["tracks"]["total"]
			limit = 100

			if total_tracks > limit:
				# only do a multiple requests to get all songs if we don't
				# already have them all as that would be a big waste

				# add tracks to existing list
				track_list = request_playlist_result["tracks"]["items"]

				is_more = True
				previous_request = request_playlist_result

				while is_more:
					next_url = previous_request["tracks"]["next"]
					print(f"Requesting {next_url}")

					try:
						next_request = requests.get(next_url, headers=request_headers)
					except requests.exceptions.RequestException as error:
						print("Playlist request error")
						print(error)
						sys.exit()
					
					next_request_result = {}
					next_request_result["tracks"] = json.loads(next_request.text)

					track_list += next_request_result["tracks"]["items"]

					if next_request_result["tracks"]["next"] == None:
						is_more = False
					else:
						previous_request = next_request_result
				
				request_playlist_result["tracks"]["items"] = track_list

			return request_playlist_result
		else:
			return False



class Downloader:
	"""
	Class to handle downloading the 30 second audio clips that the
	spotify api returns

	Args:
		threads: The number of threads that the downloader should 
				 use (Default: 8)
		
		url_list: a list of Song Objects which should contain a URL
				  variable which will be downloaded and saved using
				  the {id}.mp3 naming format
	
	Returns:
		returns a list of Song objects that which should now each contain
		a location variable where the mp3 was downloaded to
	"""

	def __init__(self, threads=8):
		self.threads = threads
		print("Starting downloader")
	
	def start(self, url_list):
		# create a thread pool using x amount of threads
		pool = ThreadPool(self.threads)
		song_list, downloaded = zip(*pool.map(self.download, url_list))

		print(f"Downloaded {downloaded.count(True)} new Files")

		# Check if assets folder exists, if not, create it
		if not os.path.exists("assets/"):
			os.makedirs("assets/")

		# terminate the thread once work has been done
		pool.close()
		pool.join()

		return song_list
	
	def download(self, song):
		url = song.url
		downloaded = False

		if url is not None:
			path = f"assets/{song.id}.mp3"
			song.location = path

			# Only download if the file doesn't already exist
			if not os.path.exists(path):
				downloaded = True

				try:
					file_data = requests.get(url).content
				except requests.exceptions.RequestException as error:
					print("Download file error")
					print(error)
					sys.exit()
				
				with open(path, "wb") as data_file:
					data_file.write(file_data)
					data_file.close()
		
		return (song, downloaded)
