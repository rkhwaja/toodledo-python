"""Implementation"""

from functools import partial
from json import dumps
from logging import debug, error

from requests_oauthlib import OAuth2Session

from .account import _AccountSchema
from .context import _ContextSchema
from .errors import ToodledoError
from .folder import _FolderSchema
from .task import _DumpTaskList, _TaskSchema

def GetAccount(session):
	"""Get the Toodledo account"""
	accountInfo = session.get(Toodledo.getAccountUrl)
	accountInfo.raise_for_status()
	return _AccountSchema().load(accountInfo.json()).data

def GetTasks(session, params):
	"""Get the tasks filtered by the given params"""
	allTasks = []
	limit = 1000 # single request limit
	start = 0
	while True:
		debug("Start: {}".format(start))
		params["start"] = start
		params["num"] = limit
		response = session.get(Toodledo.getTasksUrl, params=params)
		response.raise_for_status()
		tasks = response.json()
		if "errorCode" in tasks:
			error("Toodledo error: {}".format(tasks))
			raise ToodledoError(tasks["errorCode"])
		# the first field contains the count or the error code
		allTasks.extend(tasks[1:])
		debug("Retrieved {:,} tasks".format(len(tasks[1:])))
		if len(tasks[1:]) < limit:
			break
		start += limit
	schema = _TaskSchema()
	return [schema.load(x).data for x in allTasks]

def EditTasks(session, taskList):
	"""Change the existing tasks to be the same as the ones in the given list"""
	if len(taskList) == 0:
		return
	debug("Total tasks to edit: {}".format(len(taskList)))
	limit = 50 # single request limit
	start = 0
	while True:
		debug("Start: {}".format(start))
		listDump = _DumpTaskList(taskList[start:start + limit])
		response = session.post(Toodledo.editTasksUrl, params={"tasks": dumps(listDump)})
		response.raise_for_status()
		debug("Response: {},{}".format(response, response.text))
		taskResponse = response.json()
		if "errorCode" in taskResponse:
			raise ToodledoError(taskResponse["errorCode"])
		if len(taskList[start:start + limit]) < limit:
			break
		start += limit

def AddTasks(session, taskList):
	"""Add the given tasks"""
	if len(taskList) == 0:
		return
	limit = 50 # single request limit
	start = 0
	while True:
		debug("Start: {}".format(start))
		listDump = _DumpTaskList(taskList[start:start + limit])
		response = session.post(Toodledo.addTasksUrl, params={"tasks": dumps(listDump)})
		response.raise_for_status()
		if "errorCode" in response.json():
			raise ToodledoError(response.json()["errorCode"])
		if len(taskList[start:start + limit]) < limit:
			break
		start += limit

def DeleteTasks(session, taskList):
	"""Delete the given tasks"""
	if len(taskList) == 0:
		return
	taskIdList = [task.id_ for task in taskList]
	limit = 50 # single request limit
	start = 0
	while True:
		debug("Start: {}".format(start))
		response = session.post(Toodledo.deleteTasksUrl, params={"tasks": dumps(taskIdList[start:start + limit])})
		response.raise_for_status()
		if "errorCode" in response.json():
			raise ToodledoError(response.json()["errorCode"])
		if len(taskIdList[start:start + limit]) < limit:
			break
		start += limit

class Toodledo:
	"""Wrapper for the Toodledo v3 API"""
	tokenUrl = "https://api.toodledo.com/3/account/token.php"
	getAccountUrl = "https://api.toodledo.com/3/account/get.php"
	getTasksUrl = "https://api.toodledo.com/3/tasks/get.php"
	deleteTasksUrl = "https://api.toodledo.com/3/tasks/delete.php"
	addTasksUrl = "https://api.toodledo.com/3/tasks/add.php"
	editTasksUrl = "https://api.toodledo.com/3/tasks/edit.php"
	getFoldersUrl = "https://api.toodledo.com/3/folders/get.php"
	addFolderUrl = "https://api.toodledo.com/3/folders/add.php"
	deleteFolderUrl = "https://api.toodledo.com/3/folders/delete.php"
	editFolderUrl = "https://api.toodledo.com/3/folders/edit.php"
	getContextsUrl = "https://api.toodledo.com/3/contexts/get.php"
	addContextUrl = "https://api.toodledo.com/3/contexts/add.php"
	editContextUrl = "https://api.toodledo.com/3/contexts/edit.php"
	deleteContextUrl = "https://api.toodledo.com/3/contexts/delete.php"

	def __init__(self, clientId, clientSecret, tokenStorage, scope):
		self.tokenStorage = tokenStorage
		self.clientId = clientId
		self.clientSecret = clientSecret
		self.scope = scope
		self.session = self.Session()

	def _Authorize(self):
		authorizationBaseUrl = "https://api.toodledo.com/3/account/authorize.php"
		session = OAuth2Session(client_id=self.clientId, scope=self.scope)
		authorizationUrl, _ = session.authorization_url(authorizationBaseUrl)
		print("Go to the following URL and authorize the app:" + authorizationUrl)

		try:
			from pyperclip import copy
			copy(authorizationUrl)
			print("URL copied to clipboard")
		except ImportError:
			pass

		redirectResponse = input("Paste the full redirect URL here:")

		token = session.fetch_token(Toodledo.tokenUrl, client_secret=self.clientSecret, authorization_response=redirectResponse, token_updater=self.tokenStorage.Save)
		self.tokenStorage.Save(token)
		return token

	def Session(self):
		"""Create and return a requests OAuth2 session"""
		token = self.tokenStorage.Load()
		if token is None:
			token = self._Authorize()

		return OAuth2Session(
			client_id=self.clientId, token=token, auto_refresh_kwargs={
				"client_id": self.clientId,
				"client_secret": self.clientSecret
			}, auto_refresh_url=Toodledo.tokenUrl, token_updater=self.tokenStorage.Save)

	def _ReauthorizeIfNecessary(self, func):
		try:
			return func(self.session)
		except ToodledoError:
			# this can happen if the refresh token has expired
			self.session = self._Authorize()
			return func(self.session)

	def GetFolders(self):
		"""Get all the folders as folder objects"""
		folders = self.session.get(Toodledo.getFoldersUrl)
		folders.raise_for_status()
		schema = _FolderSchema()
		return [schema.load(x).data for x in folders.json()]

	def AddFolder(self, folder):
		"""Add folder, return the created folder"""
		response = self.session.post(Toodledo.addFolderUrl, params={"name": folder.name, "private": 1 if folder.private else 0})
		response.raise_for_status()
		if "errorCode" in response.json():
			error("Toodledo error: {}".format(response.json()))
			raise ToodledoError(response.json()["errorCode"])
		return _FolderSchema().load(response.json()[0]).data

	def DeleteFolder(self, folder):
		"""Delete folder"""
		response = self.session.post(Toodledo.deleteFolderUrl, params={"id": folder.id_})
		response.raise_for_status()
		jsonResponse = response.json()
		if "errorCode" in jsonResponse:
			error("Toodledo error: {}".format(jsonResponse))
			raise ToodledoError(jsonResponse["errorCode"])
		assert jsonResponse == {"deleted": folder.id_}, dumps(jsonResponse)

	def EditFolder(self, folder):
		"""Edits the given folder to have the given properties"""
		folderData = _FolderSchema().dump(folder).data
		response = self.session.post(Toodledo.editFolderUrl, params=folderData)
		response.raise_for_status()
		responseAsDict = response.json()
		if "errorCode" in responseAsDict:
			error("Toodledo error: {}".format(responseAsDict))
			raise ToodledoError(responseAsDict["errorCode"])
		return _FolderSchema().load(responseAsDict[0]).data

	def GetContexts(self):
		"""Get all the contexts as context objects"""
		contexts = self.session.get(Toodledo.getContextsUrl)
		contexts.raise_for_status()
		schema = _ContextSchema()
		return [schema.load(x).data for x in contexts.json()]

	def AddContext(self, context):
		"""Add context, return the created context"""
		response = self.session.post(Toodledo.addContextUrl, params={"name": context.name, "private": 1 if context.private else 0})
		response.raise_for_status()
		if "errorCode" in response.json():
			error("Toodledo error: {}".format(response.json()))
			raise ToodledoError(response.json()["errorCode"])
		return _ContextSchema().load(response.json()[0]).data

	def DeleteContext(self, context):
		"""Delete context"""
		response = self.session.post(Toodledo.deleteContextUrl, params={"id": context.id_})
		response.raise_for_status()
		jsonResponse = response.json()
		if "errorCode" in jsonResponse:
			error("Toodledo error: {}".format(jsonResponse))
			raise ToodledoError(jsonResponse["errorCode"])
		assert jsonResponse == {"deleted": context.id_}, dumps(jsonResponse)

	def EditContext(self, context):
		"""Edits the given folder to have the given properties"""
		contextData = _ContextSchema().dump(context).data
		response = self.session.post(Toodledo.editContextUrl, params=contextData)
		response.raise_for_status()
		responseAsDict = response.json()
		if "errorCode" in responseAsDict:
			error("Toodledo error: {}".format(responseAsDict))
			raise ToodledoError(responseAsDict["errorCode"])
		return _ContextSchema().load(responseAsDict[0]).data

	def GetAccount(self):
		"""Get the Toodledo account"""
		return self._ReauthorizeIfNecessary(partial(GetAccount))

	def GetTasks(self, params):
		"""Get the tasks filtered by the given params"""
		return self._ReauthorizeIfNecessary(partial(GetTasks, params=params))

	def EditTasks(self, params):
		"""Change the existing tasks to be the same as the ones in the given list"""
		self._ReauthorizeIfNecessary(partial(EditTasks, taskList=params))

	def AddTasks(self, taskList):
		"""Add the given tasks"""
		self._ReauthorizeIfNecessary(partial(AddTasks, taskList=taskList))

	def DeleteTasks(self, params):
		"""Delete the given tasks"""
		self._ReauthorizeIfNecessary(partial(DeleteTasks, taskList=params))
