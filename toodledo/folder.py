"""Account-related stuff"""
from marshmallow import fields, post_load, Schema

from .custom_fields import _ToodledoBoolean

class Folder: # pylint: disable=too-few-public-methods
	"""Toodledo folder"""
	def __init__(self, **data):
		for name, item in data.items():
			setattr(self, name, item)

	def __repr__(self):
		attributes = sorted(["{}={}".format(name, item) for name, item in self.__dict__.items()])
		return "<Folder {}>".format(", ".join(attributes))

class _FolderSchema(Schema):
	id_ = fields.Integer(dump_to="id", load_from="id")
	name = fields.String()
	private = _ToodledoBoolean()
	archived = _ToodledoBoolean()
	order = fields.Integer(dump_to="ord", load_from="ord")

	@post_load
	def _MakeFolder(self, data): # pylint: disable=no-self-use
		return Folder(**data)
