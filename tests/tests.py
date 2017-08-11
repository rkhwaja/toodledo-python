from logging import error
from os import environ
from unittest import main, TestCase

from toodledo import TokenStorageFile, Toodledo

class TestTasks(TestCase):
	def setUp(self):
		tokenStorage = TokenStorageFile("token_storage.json")
		self.toodledo = Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

	def testGetAccount(self):
		account = self.toodledo.GetAccount()
		# no crash

	def testGetTasks(self):
		tasks = self.toodledo.GetTasks(params={})

if __name__ == '__main__':
	main()
