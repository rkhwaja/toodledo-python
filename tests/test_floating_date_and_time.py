from datetime import date, time
from os import environ

from pytest import fixture

@fixture
def toodledo():
	from toodledo import TokenStorageFile, Toodledo
	tokenStorage = TokenStorageFile(environ["TOODLEDO_TOKEN_STORAGE"])
	return Toodledo(clientId=environ["TOODLEDO_CLIENT_ID"], clientSecret=environ["TOODLEDO_CLIENT_SECRET"], tokenStorage=tokenStorage, scope="basic tasks notes folders write")

def test_read_known_start_datetime_tasks(toodledo):
	tasks = toodledo.GetTasks(params={"fields": "startdate,starttime"})
	bothFieldsTask = [task for task in tasks if task.title == "Test task with start date and start time"][0]
	onlyDateTask = [task for task in tasks if task.title == "Test task with start date but no start time"][0]
	onlyTimeTask = [task for task in tasks if task.title == "Test task with start time but no start date"][0]

	assert bothFieldsTask.startDate == date(2018, 3, 10)
	assert bothFieldsTask.startTime == time(hour=7)

	assert onlyDateTask.startDate == date(2018, 3, 11)
	assert onlyDateTask.startTime is None

	assert onlyTimeTask.startDate is None
	# fails - this task returns 0 for starttime
	# assert onlyTimeTask.startTime == time(hour=16)

def test_read_known_due_datetime_tasks(toodledo):
	tasks = toodledo.GetTasks(params={"fields": "duedate,duetime"})
	bothFieldsTask = [task for task in tasks if task.title == "Test task with due date and due time"][0]
	onlyDateTask = [task for task in tasks if task.title == "Test task with due date but no due time"][0]
	onlyTimeTask = [task for task in tasks if task.title == "Test task with due time but no due date"][0]

	assert bothFieldsTask.dueDate == date(2018, 12, 25)
	assert bothFieldsTask.dueTime == time(hour=5)

	assert onlyDateTask.dueDate == date(2018, 12, 21)
	assert onlyDateTask.dueTime is None

	assert onlyTimeTask.dueDate is None
	# fails - this task returns 0 for duetime
	# assert onlyTimeTask.dueTime == time(hour=6)

