"""Implementation"""

from datetime import date, datetime
from enum import Enum
from functools import partial
from json import dump, dumps, load
from logging import debug, error

from marshmallow import fields, post_load, Schema
from marshmallow.validate import Length
from requests_oauthlib import OAuth2Session

# all the fields have the option for not being set
# dates have an extra option of being 0 or a real date

# states for this field are:
# a GMT timestamp with the time set to noon
# unset, represented by API as 0
class _ToodledoDate(fields.Field):
	def _serialize(self, value, attr, obj):
		if value is None:
			return 0
		return datetime(year=value.year, month=value.month, day=value.day).timestamp()

	def _deserialize(self, value, attr, data):
		if value == 0:
			return None
		return date.fromtimestamp(float(value))

# states for this field are:
# a GMT timestamp
# unset, represented by API as 0
class _ToodledoDatetime(fields.Field):
	def _serialize(self, value, attr, obj):
		if value is None:
			return 0
		return value.timestamp()

	def _deserialize(self, value, attr, data):
		if value == 0:
			return None
		return datetime.fromtimestamp(float(value))

class _ToodledoTags(fields.Field):
	def _serialize(self, value, attr, obj):
		assert isinstance(value, list)
		return ", ".join(sorted(value))

	def _deserialize(self, value, attr, data):
		assert isinstance(value, str)
		if value == "":
			return []
		return [x.strip() for x in value.split(",")]

class Priority(Enum):
	"""Priority as an enum with the correct Toodledo integer equivalents"""
	NEGATIVE = -1
	LOW = 0
	MEDIUM = 1
	HIGH = 2
	TOP = 3

class _ToodledoPriority(fields.Field):
	def _serialize(self, value, attr, obj):
		assert isinstance(value, Priority)
		return value.value

	def _deserialize(self, value, attr, data):
		assert isinstance(value, int)
		assert -1 <= value <= 3
		for enumValue in Priority:
			if enumValue.value == value:
				return enumValue
		assert False, "Bad incoming integer for priority enum"
		return None

class DueDateModifier(Enum):
	"""Enum for all the due date modifiers"""
	DUE_BY = 0
	DUE_ON = 1
	DUE_AFTER = 2
	OPTIONALLY = 3

class _ToodledoDueDateModifier(fields.Field):
	def _serialize(self, value, attr, obj):
		assert isinstance(value, DueDateModifier)
		return value.value

	def _deserialize(self, value, attr, data):
		assert isinstance(value, int)
		assert 0 <= value <= 3
		for enumValue in DueDateModifier:
			if enumValue.value == value:
				return enumValue
		assert False, "Bad incoming integer for due date modifier enum"
		return None

class Status(Enum):
	"""Enum for all the possible statuses"""
	NONE = 0
	NEXT_ACTION = 1
	ACTIVE = 2
	PLANNING = 3
	DELEGATED = 4
	WAITING = 5
	HOLD = 6
	POSTPONED = 7
	SOMEDAY = 8
	CANCELED = 9
	REFERENCE = 10

class _ToodledoStatus(fields.Field):
	def _serialize(self, value, attr, obj):
		assert isinstance(value, Status)
		return value.value

	def _deserialize(self, value, attr, data):
		assert isinstance(value, int)
		assert 0 <= value <= 10
		for enumValue in Status:
			if enumValue.value == value:
				return enumValue
		assert False, "Bad incoming integer for status enum"
		return None

class Task:
	"""Represents a single task"""

	def __init__(self, **data):
		for name, item in data.items():
			setattr(self, name, item)

	def __repr__(self):
		attributes = sorted(["{}={}".format(name, item) for name, item in self.__dict__.items()])
		return "<Task {}>".format(", ".join(attributes))

	def IsComplete(self):
		"""Indicate whether this task is complete"""
		return self.completedDate is not None # pylint: disable=no-member

class ToodledoError(Exception):
	"""Custom error for wrapping API error codes"""
	errorCodeToMessage = {
		1: "No access token was given",
		2: "The access token was invalid",
		3: "Too many API requests",
		4: "The API is offline for maintenance",
		101: "SSL connection is required",
		102: "There was an error requesting a token",
		103: "Too many token requests",
		601: "Your task must have a title.",
		602: "Only 50 tasks can be added/edited/deleted at a time.",
		603: "The maximum number of tasks allowed per account (20000) has been reached",
		604: "Empty id",
		605: "Invalid task",
		606: "Nothing was added/edited. You'll get this error if you attempt to edit a task but don't pass any parameters to edit.",
		607: "Invalid folder id",
		608: "Invalid context id",
		609: "Invalid goal id",
		610: "Invalid location id",
		611: "Malformed request",
		612: "Invalid parent id",
		613: "Incorrect field parameters",
		614: "Parent was deleted",
		615: "Invalid collaborator",
		616: "Unable to reassign or share task"
	}

	def __init__(self, errorCode):
		errorMessage = ToodledoError.errorCodeToMessage.get(errorCode, "Unknown error")
		super().__init__(errorMessage, errorCode)

class _TaskSchema(Schema):
	id_ = fields.Integer(dump_to="id", load_from="id")
	title = fields.String(validate=Length(max=255))
	tags = _ToodledoTags(dump_to="tag", load_from="tag")
	startDate = _ToodledoDate(dump_to="startdate", load_from="startdate")
	dueDate = _ToodledoDate(dump_to="duedate", load_from="duedate")
	modified = _ToodledoDatetime()
	completedDate = _ToodledoDate(dump_to="completed", load_from="completed")
	star = fields.Boolean(truthy=1, falsy=0)
	priority = _ToodledoPriority()
	dueDateModifier = _ToodledoDueDateModifier(dump_to="duedatemod", load_from="duedatemod")
	status = _ToodledoStatus()
	length = fields.Integer()
	note = fields.String()

	@post_load
	def _MakeTask(self, data): # pylint: disable=no-self-use
		return Task(**data)

class _Account: # pylint: disable=too-few-public-methods
	def __init__(self, lastEditTask, lastDeleteTask):
		self.lastEditTask = lastEditTask
		self.lastDeleteTask = lastDeleteTask

	def __repr__(self):
		return "<_Account lastEditTask={}, lastDeleteTask={}>".format(self.lastEditTask, self.lastDeleteTask)

class _AccountSchema(Schema):
	lastEditTask = _ToodledoDatetime(dump_to="lastedit_task", load_from="lastedit_task")
	lastDeleteTask = _ToodledoDatetime(dump_to="lastdelete_task", load_from="lastdelete_task")

	@post_load
	def _MakeAccount(self, data): # pylint: disable=no-self-use
		return _Account(data["lastEditTask"], data["lastDeleteTask"])

def _DumpTaskList(taskList):
	# TODO - pass many=True to the schema instead of this custom stuff
	schema = _TaskSchema()
	return [schema.dump(task).data for task in taskList]

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

class TokenStorageFile:
	"""Stores the API tokens as a file"""

	def __init__(self, path):
		self.path = path

	def Save(self, token):
		"""Save the given token. Called by Toodledo class"""
		with open(self.path, "w") as f:
			dump(token, f)

	def Load(self):
		"""Load and return the token. Called by Toodledo class"""
		try:
			with open(self.path, "r") as f:
				return load(f)
		except FileNotFoundError:
			return None

class Toodledo:
	"""Wrapper for the Toodledo v3 API"""
	tokenUrl = "https://api.toodledo.com/3/account/token.php"
	getAccountUrl = "https://api.toodledo.com/3/account/get.php"
	getTasksUrl = "https://api.toodledo.com/3/tasks/get.php"
	deleteTasksUrl = "https://api.toodledo.com/3/tasks/delete.php"
	addTasksUrl = "https://api.toodledo.com/3/tasks/add.php"
	editTasksUrl = "https://api.toodledo.com/3/tasks/edit.php"

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
