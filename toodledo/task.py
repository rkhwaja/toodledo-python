"""Task-related stuff"""

from marshmallow import fields, post_load, Schema
from marshmallow.validate import Length

from .custom_fields import _ToodledoBoolean, _ToodledoDate, _ToodledoDatetime, _ToodledoDueDateModifier, _ToodledoListId, _ToodledoPriority, _ToodledoStatus, _ToodledoTags

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

class _TaskSchema(Schema):
	id_ = fields.Integer(dump_to="id", load_from="id")
	title = fields.String(validate=Length(max=255))
	tags = _ToodledoTags(dump_to="tag", load_from="tag")
	startDate = _ToodledoDate(dump_to="startdate", load_from="startdate")
	dueDate = _ToodledoDate(dump_to="duedate", load_from="duedate")
	modified = _ToodledoDatetime()
	completedDate = _ToodledoDate(dump_to="completed", load_from="completed")
	star = _ToodledoBoolean()
	priority = _ToodledoPriority()
	dueDateModifier = _ToodledoDueDateModifier(dump_to="duedatemod", load_from="duedatemod")
	status = _ToodledoStatus()
	length = fields.Integer()
	note = fields.String()
	folderId = _ToodledoListId(dump_to="folder", load_from="folder")
	contextId = _ToodledoListId(dump_to="context", load_from="context")

	@post_load
	def _MakeTask(self, data): # pylint: disable=no-self-use
		return Task(**data)

def _DumpTaskList(taskList):
	# TODO - pass many=True to the schema instead of this custom stuff
	schema = _TaskSchema()
	return [schema.dump(task).data for task in taskList]
