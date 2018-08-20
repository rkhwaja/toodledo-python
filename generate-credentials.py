#! /usr/bin/env python

from os import environ

from toodledo import TokenStorageFile, Toodledo

tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])

app = Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")
