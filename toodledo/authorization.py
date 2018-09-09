"""Example authorization"""
from requests_oauthlib import OAuth2Session
from .transport import Toodledo

def CommandLineAuthorization(clientId, clientSecret, scope, tokenStorage):
	"""Authorize in a command line program"""
	authorizationBaseUrl = "https://api.toodledo.com/3/account/authorize.php"
	session = OAuth2Session(client_id=clientId, scope=scope)
	authorizationUrl, _ = session.authorization_url(authorizationBaseUrl)
	print("Go to the following URL and authorize the app:" + authorizationUrl)

	try:
		from pyperclip import copy
		copy(authorizationUrl)
		print("URL copied to clipboard")
	except ImportError:
		pass

	redirectResponse = input("Paste the full redirect URL here: ")

	token = session.fetch_token(Toodledo.tokenUrl, client_secret=clientSecret, authorization_response=redirectResponse, token_updater=tokenStorage.Save)
	tokenStorage.Save(token)
	return token
