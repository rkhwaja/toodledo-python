"""Implementation"""

from datetime import date, datetime

from marshmallow import fields

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
