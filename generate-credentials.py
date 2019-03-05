#! /usr/bin/env python

"""Generate credentials for tests"""

from os import environ

from toodledo import CommandLineAuthorization, TokenStorageFile, Toodledo

if __name__ == "__main__":

	tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])

	app = Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

	CommandLineAuthorization(environ["TOODLEDO_CLIENT_ID"], environ["TOODLEDO_CLIENT_SECRET"], "basic tasks notes folders write", tokenStorage)
