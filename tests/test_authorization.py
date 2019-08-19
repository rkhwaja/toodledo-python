# from logging import info

def test_extra_fields(toodledo):
	for i in range(101):
		tasks = toodledo.GetTasks(params={})
		# info(f"Done get {i}")