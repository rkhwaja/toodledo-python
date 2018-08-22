from datetime import date, datetime, timedelta
from os import environ
from uuid import uuid4

from pytest import fixture

from toodledo import DueDateModifier, Priority, Status, Task

@fixture
def toodledo():
	from toodledo import TokenStorageFile, Toodledo
	tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])
	return Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

def CreateATask(toodledo, task):
	task.title = str(uuid4())
	splitTime = datetime.now()
	toodledo.AddTasks([task])
	tasks = toodledo.GetTasks(params={"fields": "startdate,duedate,tag,star,priority,duedatemod,status,length,note"})
	assert isinstance(tasks, list)
	assert len(tasks) >= 1

	# find our tasks
	ourTasks = [t for t in tasks if t.title == task.title]
	assert len(ourTasks) == 1
	returnedTask = ourTasks[0]
	print(returnedTask)

	assert task.title == returnedTask.title
	assert hasattr(task, "completedDate") is False or task.completedDate is None
	assert hasattr(task, "startDate") is False or task.startDate == returnedTask.startDate
	assert hasattr(task, "dueDate") is False or task.dueDate == returnedTask.dueDate
	assert hasattr(task, "tags") is False or set(task.tags) == set(returnedTask.tags)
	assert hasattr(task, "star") is False or task.star == returnedTask.star
	assert hasattr(task, "priority") is False or task.priority == returnedTask.priority
	assert hasattr(task, "dueDateModifier") is False or task.dueDateModifier == returnedTask.dueDateModifier
	assert hasattr(task, "status") is False or task.status == returnedTask.status
	assert hasattr(task, "length") is False or task.length == returnedTask.length
	assert hasattr(task, "note") is False or task.note == returnedTask.note

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

	task = CreateATask(toodledo, Task(star=False))
	toodledo.DeleteTasks([task])

def test_existing_star(toodledo):
	tasks = toodledo.GetTasks(params={"fields": "star"})
	ourTask = [t for t in tasks if t.title == "Test task with star"][0]
	assert ourTask.star is True

def test_set_status(toodledo):
	task = CreateATask(toodledo, Task(status=Status.NEXT_ACTION))
	toodledo.DeleteTasks([task])

	task = CreateATask(toodledo, Task(status=Status.NONE))
	toodledo.DeleteTasks([task])

	task = CreateATask(toodledo, Task(status=Status.WAITING))
	toodledo.DeleteTasks([task])

def test_set_length(toodledo):
	task = CreateATask(toodledo, Task(length=42))
	toodledo.DeleteTasks([task])

def test_set_note(toodledo):
	task = CreateATask(toodledo, Task(note="This is a note"))
	toodledo.DeleteTasks([task])

def test_set_priority(toodledo):
	task = CreateATask(toodledo, Task(priority=Priority.HIGH))
	toodledo.DeleteTasks([task])

	task = CreateATask(toodledo, Task(priority=Priority.NEGATIVE))
	toodledo.DeleteTasks([task])

def test_set_due_date_modifier(toodledo):
	task = CreateATask(toodledo, Task(dueDate=date.today(), dueDateModifier=DueDateModifier.DUE_AFTER))
	toodledo.DeleteTasks([task])

	task = CreateATask(toodledo, Task(dueDate=date.today(), dueDateModifier=DueDateModifier.DUE_ON))
	toodledo.DeleteTasks([task])

def test_write_then_read(toodledo):
	randomTitle = str(uuid4())
	splitTime = datetime.now()
	toodledo.AddTasks([Task(title=randomTitle)])
	tasks = toodledo.GetTasks(params={})
	assert isinstance(tasks, list)
	assert len(tasks) >= 1

	# find our tasks
	ourTasks = [t for t in tasks if t.title == randomTitle]
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
	ourTasks = [t for t in tasks if t.title == randomTitle]
	assert len(ourTasks) == 0

def test_extra_fields(toodledo):
	randomTitle = str(uuid4())
	splitTime = datetime.now()
	toodledo.AddTasks([Task(title=randomTitle)])
	tasks = toodledo.GetTasks(params={"fields": "tag,duedate,startdate"})
	assert isinstance(tasks, list)
	assert len(tasks) >= 1

	# find our tasks
	ourTasks = [t for t in tasks if t.title == randomTitle]
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
	ourTasks = [t for t in tasks if t.title == randomTitle]
	assert len(ourTasks) == 0
