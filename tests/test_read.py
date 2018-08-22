from json import loads
from os import environ

from pytest import fixture

class TokenReadOnly:
	"""Read the API tokens from an environment variable"""

	def __init__(self, name):
		self.name = name

	def Save(self, token):
		"""Do nothing - this may cause a problem if the refresh token changes"""
		return

	def Load(self):
		"""Load and return the token. Called by Toodledo class"""
		return loads(environ[self.name])

@fixture
def toodledo():
	from toodledo import TokenStorageFile, Toodledo
	if "TOODLEDO_TOKEN_STORAGE" in environ:
		tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])
	else:
		# for travis
		tokenStorage = TokenReadOnly("TOODLEDO_TOKEN_READONLY")
	return Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

def test_get_account(toodledo):
	account = toodledo.GetAccount()

def test_get_tasks(toodledo):
	tasks = toodledo.GetTasks(params={})
	assert isinstance(tasks, list)
