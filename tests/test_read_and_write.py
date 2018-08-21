from datetime import datetime, timedelta
from os import environ
from uuid import uuid4

from pytest import fixture

from toodledo import Task

@fixture
def toodledo():
	from toodledo import TokenStorageFile, Toodledo
	tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])
	return Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

def test_write_then_read(toodledo):
	randomTitle = str(uuid4())
	splitTime = datetime.now()
	toodledo.AddTasks([Task(title=randomTitle)])
	tasks = toodledo.GetTasks(params={})
	assert isinstance(tasks, list)
	assert len(tasks) >= 1

	# find our tasks - toodledo times don't have fractional seconds so we might have to go back 1 second
	ourTasks = [task for task in tasks if task.modified >= splitTime - timedelta(seconds=1)]
	assert len(ourTasks) == 1
	task = ourTasks[0]

	assert hasattr(task, "title")
	assert hasattr(task, "id_")
	assert hasattr(task, "modified")
	assert hasattr(task, "completedDate")
	assert not hasattr(task, "startDate")
	assert not hasattr(task, "dueDate")
	assert not hasattr(task, "tags")

	assert task.title == randomTitle

	# clean up
	toodledo.DeleteTasks([task])

	# find our tasks again
	tasks = toodledo.GetTasks(params={})
	ourTasks = [task for task in tasks if task.modified >= splitTime - timedelta(seconds=1)]
	assert len(ourTasks) == 0

def test_extra_fields(toodledo):
	randomTitle = str(uuid4())
	splitTime = datetime.now()
	toodledo.AddTasks([Task(title=randomTitle)])
	tasks = toodledo.GetTasks(params={"fields": "tag,duedate,startdate"})
	assert isinstance(tasks, list)
	assert len(tasks) >= 1

	# find our tasks - toodledo times don't have fractional seconds so we might have to go back 1 second
	ourTasks = [task for task in tasks if task.modified >= splitTime - timedelta(seconds=1)]
	assert len(ourTasks) == 1
	task = ourTasks[0]

	assert hasattr(task, "title")
	assert hasattr(task, "id_")
	assert hasattr(task, "modified")
	assert hasattr(task, "completedDate")
	assert hasattr(task, "startDate")
	assert hasattr(task, "dueDate")
	assert hasattr(task, "tags")

	assert task.title == randomTitle

	# clean up
	toodledo.DeleteTasks([task])

	# find our tasks again
	tasks = toodledo.GetTasks(params={})
	ourTasks = [task for task in tasks if task.modified >= splitTime - timedelta(seconds=1)]
	assert len(ourTasks) == 0
