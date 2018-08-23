from uuid import uuid4

from toodledo import Folder

# There's no export for these in the toodledo web interface so the user will have to make them themselves
def test_get_known_folders(toodledo):
	folders = toodledo.GetFolders()
	assert isinstance(folders, list)
	assert len(folders) == 3
	folder = folders[0]
	assert folder.name == "Test Folder"
	assert folder.archived is False
	assert folder.order == 1
	assert folder.private is False

	assert folders[1].name == "Test Folder - archived"
	assert folders[1].archived is True
	assert folders[1].private is False

	assert folders[2].name == "Test Folder - private"
	assert folders[2].archived is False
	assert folders[2].private is True

def test_add_edit_delete_folder(toodledo):
	randomName = str(uuid4())
	newFolder = toodledo.AddFolder(Folder(name=randomName, private=False))
	assert isinstance(newFolder, Folder)
	assert newFolder.name == randomName
	assert newFolder.private is False
	assert newFolder.archived is False

	newFolder.name = str(uuid4())
	newFolder.private = True
	newFolder.archived = True

	editedFolder = toodledo.EditFolder(newFolder)
	assert isinstance(editedFolder, Folder)
	assert editedFolder.id_ == newFolder.id_
	assert editedFolder.name == newFolder.name

	assert editedFolder.private == newFolder.private
	assert editedFolder.archived == newFolder.archived

	allFolders = toodledo.GetFolders()
	ourFolder = [f for f in allFolders if f.id_ == newFolder.id_][0]
	assert ourFolder.id_ == newFolder.id_
	assert ourFolder.name == newFolder.name

	assert ourFolder.private == newFolder.private
	assert ourFolder.archived == newFolder.archived

	toodledo.DeleteFolder(editedFolder)
