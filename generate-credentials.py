#! /usr/bin/env python

"""Generate credentials for tests and updating Travis"""

from contextlib import suppress
from os import environ

from toodledo import CommandLineAuthorization, TokenStorageFile, Toodledo

def EscapeForBash(token):
	charactersToEscape = "{}\"[]: "
	for character in charactersToEscape:
		token = token.replace(character, "\\" + character)
	return token

if __name__ == "__main__":

	tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])

	app = Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

	CommandLineAuthorization(environ["TOODLEDO_CLIENT_ID"], environ["TOODLEDO_CLIENT_SECRET"], "basic tasks notes folders write", tokenStorage)

	with suppress(ImportError):
		from pyperclip import copy
		with open(environ["TOODLEDO_TOKEN_STORAGE"]) as f:
			token = f.read()
		token = EscapeForBash(token)
		copy(token)
		print("Escaped token copied to clipboard - update Travis TOODLEDO_TOKEN_READONLY environment variable")
