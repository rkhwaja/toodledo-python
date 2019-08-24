from json import loads
from logging import info
from os import environ

from pytest import fixture
from travis_env import travis_env

from toodledo import TokenStorageFile, Toodledo

def EscapeForBash(token):
	charactersToEscape = "{}\"[]: "
	for character in charactersToEscape:
		token = token.replace(character, "\\" + character)
	return token

class TokenReadOnly:
	"""Read the API tokens from an environment variable"""

	def __init__(self):
		self.token = self.Load()

	def Save(self, token): # pylint: disable=no-self-use
		"""Do nothing - this may cause a problem if the refresh token changes"""
		travis_env.update(environ["TRAVIS_REPO"], TOODLEDO_TOKEN_READONLY=EscapeForBash(token))

	def Load(self): # pylint: disable=no-self-use
		"""Load and return the token. Called by Toodledo class"""
		travisRepo = environ["TRAVIS_REPO"]
		info(f"travisRepo: {travisRepo}")
		allVars = travis_env.vars(travisRepo)
		info(f"allVars: {allVars}")
		test_var = allVars["test_var"]
		info(f"test_var: {test_var}")
		assert loads(test_var)["A"] == "&"
		return loads(allVars["TOODLEDO_TOKEN_READONLY"])

@fixture
def toodledo():
	if "TOODLEDO_TOKEN_STORAGE" in environ:
		tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])
	else:
		# for travis
		tokenStorage = TokenReadOnly()
	return Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")
