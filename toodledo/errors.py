"""Known Toodledo errors"""

class ToodledoError(Exception):
	"""Custom error for wrapping API error codes"""
	errorCodeToMessage = {
		1: "No access token was given",
		2: "The access token was invalid",
		3: "Too many API requests",
		4: "The API is offline for maintenance",
		101: "SSL connection is required",
		102: "There was an error requesting a token",
		103: "Too many token requests",
		201: "Your folder must have a name.",
		202: "A folder with that name already exists.",
		203: "Max folders reached (1000).",
		204: "Empty id.",
		205: "Invalid folder.",
		206: "Nothing was edited.",
		301: "Your context must have a name.",
		302: "A context with that name already exists.",
		303: "Max contexts reached (1000).",
		304: "Empty id.",
		305: "Invalid context.",
		306: "Nothing was edited.",
		601: "Your task must have a title.",
		602: "Only 50 tasks can be added/edited/deleted at a time.",
		603: "The maximum number of tasks allowed per account (20000) has been reached",
		604: "Empty id",
		605: "Invalid task",
		606: "Nothing was added/edited. You'll get this error if you attempt to edit a task but don't pass any parameters to edit.",
		607: "Invalid folder id",
		608: "Invalid context id",
		609: "Invalid goal id",
		610: "Invalid location id",
		611: "Malformed request",
		612: "Invalid parent id",
		613: "Incorrect field parameters",
		614: "Parent was deleted",
		615: "Invalid collaborator",
		616: "Unable to reassign or share task"
	}

	def __init__(self, errorCode):
		errorMessage = ToodledoError.errorCodeToMessage.get(errorCode, "Unknown error")
		super().__init__(errorMessage, errorCode)
