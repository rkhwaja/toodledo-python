"""Account-related stuff"""
from marshmallow import fields, post_load, Schema

from .custom_fields import _ToodledoBoolean

class Context: # pylint: disable=too-few-public-methods
	"""Toodledo context"""
	def __init__(self, **data):
		for name, item in data.items():
			setattr(self, name, item)

	def __repr__(self):
		attributes = sorted(["{}={}".format(name, item) for name, item in self.__dict__.items()])
		return "<Context {}>".format(", ".join(attributes))

class _ContextSchema(Schema):
	id_ = fields.Integer(dump_to="id", load_from="id")
	name = fields.String()
	private = _ToodledoBoolean()

	@post_load
	def _MakeContext(self, data): # pylint: disable=no-self-use
		return Context(**data)
