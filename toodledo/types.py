"""Python-side Toodledo types"""

from enum import Enum

class Priority(Enum):
	"""Priority as an enum with the correct Toodledo integer equivalents"""
	NEGATIVE = -1
	LOW = 0
	MEDIUM = 1
	HIGH = 2
	TOP = 3

class DueDateModifier(Enum):
	"""Enum for all the due date modifiers"""
	DUE_BY = 0
	DUE_ON = 1
	DUE_AFTER = 2
	OPTIONALLY = 3

class Status(Enum):
	"""Enum for all the possible statuses"""
	NONE = 0
	NEXT_ACTION = 1
	ACTIVE = 2
	PLANNING = 3
	DELEGATED = 4
	WAITING = 5
	HOLD = 6
	POSTPONED = 7
	SOMEDAY = 8
	CANCELED = 9
	REFERENCE = 10
