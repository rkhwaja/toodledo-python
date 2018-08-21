from datetime import date, datetime, timedelta
from os import environ
from uuid import uuid4

from pytest import fixture

from toodledo import Priority, Task

@fixture
def toodledo():
	from toodledo import TokenStorageFile, Toodledo
	tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])
	return Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

def CreateATask(toodledo, task):
	task.title = str(uuid4())
	splitTime = datetime.now()
	toodledo.AddTasks([task])
	tasks = toodledo.GetTasks(params={"fields": "startdate,duedate,tag,star,priority"})
	assert isinstance(tasks, list)
	assert len(tasks) >= 1

	# find our tasks - toodledo times don't have fractional seconds so we might have to go back 1 second
	ourTasks = [task for task in tasks if task.modified >= splitTime - timedelta(seconds=1)]
	assert len(ourTasks) == 1
	returnedTask = ourTasks[0]
	print(returnedTask)

	assert task.title == returnedTask.title
	assert hasattr(task, "completedDate") is False or task.completedDate is None
	assert hasattr(task, "startDate") is False or task.startDate == returnedTask.startDate
	assert hasattr(task, "dueDate") is False or task.dueDate == returnedTask.dueDate
	assert hasattr(task, "tags") is False or set(task.tags) == set(returnedTask.tags)

	return returnedTask

def test_set_start_date(toodledo):
	task = CreateATask(toodledo, Task(startDate=date.today()))
	toodledo.DeleteTasks([task])

def test_set_due_date(toodledo):
	task = CreateATask(toodledo, Task(dueDate=date.today()))
	toodledo.DeleteTasks([task])

def test_set_tags(toodledo):
	task = CreateATask(toodledo, Task(tags=["a", "b", "c"]))
	toodledo.DeleteTasks([task])

	task = CreateATask(toodledo, Task(tags=["z", "a", "b", "c"]))
	toodledo.DeleteTasks([task])

def test_set_star(toodledo):
	task = CreateATask(toodledo, Task(star=True))
	toodledo.DeleteTasks([task])

def test_set_priority(toodledo):
	task = CreateATask(toodledo, Task(priority=Priority.HIGH))
	toodledo.DeleteTasks([task])

	task = CreateATask(toodledo, Task(priority=Priority.NEGATIVE))
	toodledo.DeleteTasks([task])

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
