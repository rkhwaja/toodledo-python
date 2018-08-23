"""Implementation"""

from datetime import date, datetime

from marshmallow import fields

from .types import DueDateModifier, Priority, Status

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

# Can't use the standard marshmallow boolean because it serializes to True/False rather than 1/0
class _ToodledoBoolean(fields.Field):
	def _serialize(self, value, attr, obj):
		assert isinstance(value, bool)
		return 1 if value else 0

	def _deserialize(self, value, attr, data):
		assert isinstance(value, int)
		assert 0 <= value <= 1
		return value == 1

class _ToodledoListId(fields.Field):
	def _serialize(self, value, attr, obj):
		assert value is None or isinstance(value, int)
		return value if value is not None else 0

	def _deserialize(self, value, attr, data):
		assert isinstance(value, int)
		if value == 0:
			return None
		return value

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
