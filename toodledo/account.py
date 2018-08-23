"""Account-related stuff"""
from marshmallow import post_load, Schema

from .custom_fields import _ToodledoDatetime

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
