"""Token storage"""

from json import dump, load

class TokenStorageFile:
	"""Stores the API tokens as a file"""

	def __init__(self, path):
		self.path = path

	def Save(self, token):
		"""Save the given token. Called by Toodledo class"""
		with open(self.path, "w") as f:
			dump(token, f)

	def Load(self):
		"""Load and return the token. Called by Toodledo class"""
		try:
			with open(self.path, "r") as f:
				return load(f)
		except FileNotFoundError:
			return None
