def test_extra_fields(toodledo):
	for _ in range(101):
		_ = toodledo.GetTasks(params={})
