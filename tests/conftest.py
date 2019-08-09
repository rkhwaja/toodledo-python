from json import loads
from os import environ

from pytest import fixture

from toodledo import TokenStorageFile, Toodledo

class TokenReadOnly:
	"""Read the API tokens from an environment variable"""

	def __init__(self, name):
		self.name = name
		self.token = self.Load()

	def Save(self, token): # pylint: disable=no-self-use
		"""Do nothing - this may cause a problem if the refresh token changes"""
		self.token = token

	def Load(self):
		"""Load and return the token. Called by Toodledo class"""
		return loads(environ[self.name])

@fixture
def toodledo():
	if "TOODLEDO_TOKEN_STORAGE" in environ:
		tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])
	else:
		# for travis
		tokenStorage = TokenReadOnly("TOODLEDO_TOKEN_READONLY")
	return Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")
