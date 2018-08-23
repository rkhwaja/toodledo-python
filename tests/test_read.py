def test_get_account(toodledo):
	_ = toodledo.GetAccount()

def test_get_tasks(toodledo):
	tasks = toodledo.GetTasks(params={})
	assert isinstance(tasks, list)

def test_get_tasks_with_known_folders(toodledo):
	folders = toodledo.GetFolders()
	tasks = toodledo.GetTasks(params={"fields": "folder"})
	taskWithPrivateFolder = [t for t in tasks if t.title == "Test task with private folder"][0]
	taskWithPublicFolder = [t for t in tasks if t.title == "Test task with public folder"][0]
	privateFolderId = [f.id_ for f in folders if f.name == "Test Folder - private"][0]
	publicFolderId = [f.id_ for f in folders if f.name == "Test Folder"][0]

	assert taskWithPrivateFolder.folderId == privateFolderId
	assert taskWithPublicFolder.folderId == publicFolderId

def test_get_tasks_with_known_contexts(toodledo):
	contexts = toodledo.GetContexts()
	tasks = toodledo.GetTasks(params={"fields": "context"})
	taskWithPrivateContext = [t for t in tasks if t.title == "Test task with private context"][0]
	taskWithPublicContext = [t for t in tasks if t.title == "Test task with public context"][0]
	privateContextId = [x.id_ for x in contexts if x.name == "Test Context - private"][0]
	publicContextId = [x.id_ for x in contexts if x.name == "Test Context - public"][0]

	assert taskWithPrivateContext.contextId == privateContextId
	assert taskWithPublicContext.contextId == publicContextId
