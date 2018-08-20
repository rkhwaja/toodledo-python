from os import environ

from pytest import fixture

@fixture
def toodledo():
	from toodledo import TokenStorageFile, Toodledo
	tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])
	return Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

def test_get_account(toodledo):
	account = toodledo.GetAccount()

def test_get_tasks(toodledo):
	tasks = toodledo.GetTasks(params={})
	assert isinstance(tasks, list)
